import logging
import mimetypes
import re
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.datastructures import FormData
from fastapi_cache.decorator import cache

import config
from src.api.picwish import Picwish
from src.auth.login import admin_resource
from src.database import mongo
from src.helpers.download import download_file
from src.helpers.string import snake_case
from src.models.client import CRM, ClientInfoModel, ClientModel, Colors, Prospector
from src.models.niches import segmented_models

router = APIRouter(prefix="/clients", tags=["Client"])


@router.get("/")
@cache(expire=60)
async def get_clients(
    _: ClientModel = Depends(admin_resource),
    skip: int = Query(0),
    limit: int = Query(12),
    search_term: str = Query(alias="searchTerm", default=None),
    niche: str = Query(None),
    payment_type: str = Query(None, alias="paymentType"),
    is_dev: bool = Query(False, alias="isDev"),
    exclude_dev: bool = Query(False, alias="excludeDev"),
    sellers: str = Query(None),
):
    query = {}

    if search_term:
        query = {
            "$or": [
                {"client": {"$regex": search_term, "$options": "i"}},
                {"info.name": {"$regex": search_term, "$options": "i"}},
                {"info.email": {"$regex": search_term, "$options": "i"}},
                {"info.cellphone": {"$regex": search_term, "$options": "i"}},
                {"info.instagram": {"$regex": search_term, "$options": "i"}},
            ]
        }

    if niche:
        query["niche"] = {"$in": niche.split(",")}

    if payment_type:
        query["purchase.type"] = {"$in": payment_type.split(",")}

    if sellers:
        query["prospector.cellphone"] = {"$in": sellers.split(",")}

    if is_dev:
        query["is_dev"] = is_dev

    if exclude_dev:
        query["is_dev"] = {"$ne": exclude_dev}

    count = await mongo.database.clients.count_documents(query)

    clients = (
        await mongo.database.clients.find(query)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )

    for client in clients:
        client["id"] = str(client.pop("_id"))

    return {"count": count, "clients": clients, "pages": count // limit}


def parse_form(form: FormData):
    parsed_data = {}

    for key, value in form.items():
        parts = [part for part in re.split(r"\[|\]", key) if part]

        if "[]" in key:
            value = form.getlist(key)
            key = key.replace("[]", "")

        if value == "true":
            value = True
        elif value == "false":
            value = False

        if len(parts) > 1:
            current_level = parsed_data

            for i, part in enumerate(parts):
                part = snake_case(part)

                if i == len(parts) - 1:
                    current_level[part] = value
                else:
                    if part not in current_level:
                        current_level[part] = {}

                    current_level = current_level[part]

        else:
            parsed_data[snake_case(key)] = value

    return parsed_data


@router.put("/{client}")
async def update_client(
    request: Request, client: str, _: ClientModel = Depends(admin_resource)
):
    data = parse_form(await request.form())
    client = await mongo.database.clients.find_one({"client": client})

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    phone = client.get("main_client", client.get("client"))
    phone = phone[0] if isinstance(phone, list) else phone

    new_phone = data.get("main_client", data.get("client"))
    new_phone = new_phone[0] if isinstance(new_phone, list) else new_phone

    logo_light = data.get("light_logo")
    logo_dark = data.get("dark_logo")

    if (
        logo_light
        and logo_light.content_type not in ["image/png", "image/jpeg", "image/jpg"]
    ) or (
        logo_dark
        and logo_dark.content_type not in ["image/png", "image/jpeg", "image/jpg"]
    ):
        raise HTTPException(status_code=400, detail="Invalid file type")

    tmp_path = config.TMP_PATH / uuid.uuid4().hex
    tmp_path.mkdir(parents=True, exist_ok=True)

    client_images_path: Path = config.ABS_PATH / "data/clients/images" / phone
    new_client_images_path: Path = config.ABS_PATH / "data/clients/images" / new_phone

    client_audios_path: Path = config.ABS_PATH / "data/clients/audios" / phone
    new_client_audios_path: Path = config.ABS_PATH / "data/clients/audios" / new_phone

    if client_images_path.exists():
        shutil.move(client_images_path, new_client_images_path)

    client_images_path.mkdir(parents=True, exist_ok=True)

    if client_audios_path.exists():
        shutil.move(client_audios_path, new_client_audios_path)

    client_audios_path.mkdir(parents=True, exist_ok=True)

    try:
        segmented_data = segmented_models(data.get("niche"))

        extra_info = {}

        if segmented_data:
            extra_info = segmented_data(**data).model_dump()

        client_info = ClientInfoModel(**data, extra=extra_info)
        logo_modified = False

        if logo_light and (logo_light_contents := await logo_light.read()):
            ext = mimetypes.guess_extension(logo_light.content_type) or ".png"

            path = tmp_path / f"logo-light{ext}"
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as f:
                f.write(logo_light_contents)

            logo_url = Picwish().process_image(path)

            removed_bg_path = await download_file(logo_url, tmp_path)

            shutil.move(
                removed_bg_path,
                client_images_path / "logo.png",
            )

            logo_modified = True

        if logo_dark and (logo_dark_contents := await logo_dark.read()):
            ext = mimetypes.guess_extension(logo_dark.content_type) or ".png"

            path = tmp_path / f"logo-dark{ext}"
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "wb") as f:
                f.write(logo_dark_contents)

            logo_url = Picwish().process_image(path)

            removed_bg_path = await download_file(logo_url, tmp_path)

            shutil.move(
                removed_bg_path,
                client_images_path / "dark-logo.png",
            )

            logo_modified = True

        client_has_logo = client.get("has_logo", False)

        if logo_modified:
            client_has_logo = True

        narration_obj = client.get("narration", {})

        current_company_genre = narration_obj.get("company_genre", "")
        current_company_name = narration_obj.get("company_name", "")
        current_number_narration = narration_obj.get("number_narration", "")

        company_genre = data.get("company_genre", current_company_genre)
        company_name = data.get("company_name_narration", current_company_name)
        number_narration = data.get("number_narration", current_number_narration)

        number_ne = number_narration != current_number_narration
        company_name_ne = (
            company_genre != current_company_genre
            or company_name != current_company_name
        )

        if number_ne or company_name_ne:
            narration_obj["company_genre"] = company_genre
            narration_obj["company_name"] = company_name
            narration_obj["number_narration"] = number_narration

            for audio in new_client_audios_path.rglob("*.mp3"):
                if number_ne and audio.name.startswith("call-us"):
                    audio.unlink(missing_ok=True)

                if company_name_ne and audio.name.startswith(
                    ("opening-", "call-us-", "slogan-")
                ):
                    audio.unlink(missing_ok=True)

        use_limit = data.get(
            "use_limit", client.get("purchase", {}).get("use_limit", 0)
        )

        if not str(use_limit).isdigit():
            raise Exception("Use limit must be a number")
        elif int(use_limit) < 0:
            raise Exception("Use limit must be greater than or equal to 0")

        current_prospector = client.get("prospector", {})
        new_prospector_phone = data.get("prospector", "")
        new_prospector = current_prospector

        if new_prospector_phone:
            if new_prospector_phone != current_prospector.get("cellphone", ""):
                seller = await mongo.database.sellers.find_one(
                    {"phone": new_prospector_phone}
                )

                if seller:
                    new_prospector = Prospector(
                        name=seller.get("name", ""),
                        cellphone=new_prospector_phone,
                    ).model_dump()
                else:
                    logging.warning(
                        f"Prospector with phone {new_prospector_phone} not found. Retaining existing prospector."
                    )

        await mongo.database.clients.update_one(
            {"client": phone},
            {
                "$set": {
                    "main_client": new_phone,
                    "narration": narration_obj,
                    "client": data.get("client"),
                    "info": client_info.model_dump(),
                    "purchase.type": data.get("purchase_status", "free"),
                    "purchase.use_limit": int(use_limit),
                    "has_logo": data.get("has_logo", False),
                    "logo_by_designer": data.get("logo_by_designer", False),
                    "prospector": new_prospector,
                    "crm": CRM(
                        **{
                            **client.get("crm", {}),
                            **{
                                "id": data.get("crm_id"),
                                "deal_id": data.get("crm_deal_id"),
                                "funnel_id": data.get("crm_funnel_id"),
                                "funnel_stage": data.get("crm_funnel_stage"),
                            },
                        },
                    ).model_dump(),
                    "has_logo": client_has_logo,
                    "colors": Colors(
                        **{
                            **client.get("colors", {}),
                            **{
                                "primary": {
                                    "light": data.get("primary_color_light"),
                                    "dark": data.get("primary_color_dark"),
                                },
                                "secondary": {
                                    "light": data.get("secondary_color_light"),
                                    "dark": data.get("secondary_color_dark"),
                                },
                                "tertiary": {
                                    "light": data.get("tertiary_color_light"),
                                    "dark": data.get("tertiary_color_dark"),
                                },
                            },
                        }
                    ).model_dump(),
                }
            },
        )
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        shutil.rmtree(tmp_path)

    return {"message": "Client updated successfully"}
