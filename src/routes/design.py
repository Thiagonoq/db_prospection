import base64
import json
import logging
import uuid
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib import response

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import storage
from pydantic import BaseModel, Field

from config import FIREBASE_STORAGE_BUCKET, TMP_PATH, VIDEOAI_API_TOKEN
from src.api.picwish import Picwish
from src.api.request import Requests
from src.auth.login import get_current_user
from src.database import mongo
from src.helpers import date
from src.helpers.download import download_file
from src.helpers.string import slugify
from src.models.client import ClientModel
from src.routes.assets import AssetOrigin

router = APIRouter(prefix="/design", tags=["Design"])


class TextResize(BaseModel):
    text: str
    width: float
    height: float
    font_size: float = Field(alias="fontSize")
    font_style: str = Field(alias="fontStyle")
    line_height: float = Field(alias="lineHeight")
    font_family: str = Field(alias="fontFamily")
    font_weight: str = Field(alias="fontWeight")
    letter_spacing: float = Field(alias="letterSpacing")


class ImageAdjustment(str, Enum):
    contain = "contain"
    cover = "cover"


class ImageResize(BaseModel):
    image: dict
    image_url: str = Field(alias="imageUrl")
    adjustment: Optional[ImageAdjustment] = ImageAdjustment.contain


class PriceResize(BaseModel):
    price: list
    integer: int
    decimal: int


requests = Requests()


@router.post("/textResize")
async def text_resize(
    text_data: TextResize, _: ClientModel = Depends(get_current_user)
):
    config = await mongo.get_config()

    endpoint = config.get("art_api_endpoint")

    if not endpoint:
        raise HTTPException(status_code=500, detail="Art API endpoint not found")

    return requests.post(
        f"{endpoint}/textResize",
        json=text_data.model_dump(),
        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
    )


@router.post("/imageResize")
async def image_resize(
    image_data: ImageResize, _: ClientModel = Depends(get_current_user)
):
    config = await mongo.get_config()

    endpoint = config.get("art_api_endpoint")

    if not endpoint:
        raise HTTPException(status_code=500, detail="Art API endpoint not found")

    return requests.post(
        f"{endpoint}/imageResize",
        json=image_data.model_dump(),
        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
    )


@router.post("/priceResize")
async def price_resize(
    price_data: PriceResize, _: ClientModel = Depends(get_current_user)
):
    config = await mongo.get_config()

    endpoint = config.get("art_api_endpoint")

    if not endpoint:
        raise HTTPException(status_code=500, detail="Art API endpoint not found")

    return requests.post(
        f"{endpoint}/priceResize",
        json=price_data.model_dump(),
        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
    )


class ProcessImage(BaseModel):
    image: dict
    image_base64: str = Field(alias="imageBase64")
    categories: Optional[list] = Field(default=[], alias="categories")
    name: Optional[str] = None


@router.post("/processImage")
async def process_image(
    data: ProcessImage, client: ClientModel = Depends(get_current_user)
):
    config = await mongo.get_config()

    endpoint = config.get("art_api_endpoint")

    if not endpoint:
        raise HTTPException(status_code=500, detail="Art API endpoint not found")

    tmp_path = TMP_PATH / uuid.uuid4().hex

    mimetype, base64_str = data.image_base64.split(";base64,")

    extension = mimetype.split("/")[-1]

    tmp_path = tmp_path.with_suffix(f".{extension}")

    with open(tmp_path, "wb") as f:
        f.write(base64.b64decode(base64_str))

    url = Picwish().process_image(tmp_path)

    image_bytes = (await download_file(url, tmp_path, extension, get_bytes=True))[
        "bytes"
    ]

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    image_data = ImageResize(
        image=data.image, imageUrl=f"data:image/png;base64,{image_base64}"
    )

    response = requests.post(
        f"{endpoint}/imageResize",
        json=image_data.model_dump(),
        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
    )

    new_image_base64 = response["src"].split(";base64,")[-1]

    new_image_bytes = base64.b64decode(new_image_base64)

    mime_type = "image/png"
    image_file_size = len(new_image_bytes)
    filename = Path(f"{uuid.uuid4().hex}.png")
    slugfied_name = slugify(filename.stem)
    full_location = f"assets/personal/{client.id}/{slugfied_name}.png"

    bucket_name = FIREBASE_STORAGE_BUCKET

    bucket = storage.bucket(bucket_name)

    blob = bucket.blob(full_location)

    blob.upload_from_string(image_bytes, content_type=mime_type)

    blob.make_public()

    image_url = blob.public_url

    file_data = {
        "file": {
            "size": image_file_size,
            "filename": filename.name,
            "mimetype": mime_type,
        },
        "bucket": bucket_name,
        "url": image_url,
        "location": full_location,
        "type": "image",
        "origin": AssetOrigin.firebase,
        "is_public": False,
        "niche": client.niche,
        "name": data.name or filename.stem,
        "created_at": date.now(),
        "updated_at": date.now(),
        "options": {},
        "categories": [ObjectId(category) for category in data.categories],
    }

    if not client.is_dev:
        file_data.update(
            {
                "owner": client.client,
            }
        )

    result = await mongo.database.assets.insert_one(file_data)

    if result.inserted_id is None:
        logging.error("Failed to insert asset to database")
        logging.error(json.dumps(file_data))

    return {
        "image": response,
        "asset": {
            "id": str(result.inserted_id),
            "name": file_data["name"],
            "url": file_data["url"],
            "type": file_data["type"],
            "categories": [
                {
                    "id": str(category["_id"]),
                    "name": category["name"],
                    "slug": category["slug"],
                }
                for category in await mongo.database.categories.find(
                    {"_id": {"$in": file_data["categories"]}}
                ).to_list(None)
            ],
        },
    }
