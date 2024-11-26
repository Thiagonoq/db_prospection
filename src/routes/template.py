import logging
import re
from copy import deepcopy
from typing import Any, Optional, Union

from bson import ObjectId
from matplotlib.colors import to_rgba
from pydantic import BaseModel, Field

from config import VIDEOAI_API_TOKEN
from src.api.request import Requests
from src.database.mongo import mongo
from src.handlers.product import get_product_data
from src.models.client import ClientModel
from src.routes.design import ImageResize, PriceResize, TextResize



class TemplateIA(BaseModel):
    prompt: str
    template_id: Optional[str] = Field(None, alias="templateId")
    files: Optional[list[str]] = Field(
        None,
        alias="files",
        title="Files",
        description="Files to identify the image as base64",
        max_length=10,
    )


def get_color(color: str, client: ClientModel):
    color_name, color_variation = "".join(
        f"_{char.lower()}" if char.isupper() else char
        for char in str(color).split(".")[-1]
    ).split("_")

    default_color = "#a4ff63"

    try:
        color = getattr(getattr(client.colors, color_name), color_variation)
    except Exception as e:
        logging.info(f"The client {client.main_client} does not have the color {color}")

        try:
            color = client.colors.primary.light
        except:
            color = default_color

    if not color:
        color = default_color

    return map(
        lambda x: x * 255,
        to_rgba(color),
    )


async def process_design(
    design: dict,
    client: ClientModel,
    config: dict,
    user_data: Union[dict, list] = {},
    categories: list = [],
    bounds: dict = {},
    saved_data: dict = {},
    saved_change_data: dict = {},
):
    endpoint = config.get("art_api_endpoint")

    element_type = design.get("type")
    custom_data = design.get("custom", {})

    element_id = design.get("id")

    bound_id = custom_data.get("boundId")
    typed_element = custom_data.get("elementType")

    requests = Requests(return_default={})

    if not design.get("custom"):
        design["custom"] = {}

    if not client.is_dev:
        design["removable"] = False
        design["draggable"] = False
        design["styleEditable"] = False

    if not element_type and not client.is_dev:
        design["selectable"] = False

    if custom_data and not custom_data.get("originalAttrs"):
        original_attrs = deepcopy(design)

        delete_attrs = [
            "src",
            "text",
            "fill",
            "children",
            "pages",
            "custom",
            "type",
            "selectable",
            "removable",
            "draggable",
            "styleEditable",
            "cropWidth",
            "cropHeight",
            "cropX",
            "cropY",
        ]

        for attr in delete_attrs:
            if original_attrs.get(attr):
                del original_attrs[attr]

        design["custom"]["originalAttrs"] = original_attrs

    if (pages := design.get("pages")) and isinstance(pages, list):
        _pages = []

        for page in pages:
            _design, saved_change_data = await process_design(
                page,
                client,
                config,
                user_data,
                categories,
                page.get("custom", {}).get("bounds", {}),
                saved_data=saved_data,
                saved_change_data=saved_change_data,
            )

            _pages.append(_design)
    elif (childrens := design.get("children")) and isinstance(childrens, list):
        for index, item in enumerate(childrens):
            if not client.is_dev:
                item["removable"] = False
                item["draggable"] = False
                item["styleEditable"] = False

            item_custom_data = item.get("custom", {})

            if not item_custom_data.get("elementType") and not client.is_dev:
                design["selectable"] = False

            if item_custom_data and not item_custom_data.get("originalAttrs"):
                original_attrs = deepcopy(item)

                delete_attrs = [
                    "src",
                    "text",
                    "fill",
                    "children",
                    "pages",
                    "custom",
                    "type",
                    "selectable",
                    "removable",
                    "draggable",
                    "styleEditable",
                    "cropWidth",
                    "cropHeight",
                    "cropX",
                    "cropY",
                ]

                for attr in delete_attrs:
                    if original_attrs.get(attr):
                        del original_attrs[attr]

                item["custom"]["originalAttrs"] = original_attrs

            design["children"][index] = item

        if user_data and categories and bound_id and bounds:
            if type(bounds) == dict:
                bound = bounds.get(bound_id)
            else:
                find_element = filter(lambda item: item.get("id") == bound_id, bounds)

                bound = next(find_element, {})

            bound_type = bound.get("elementType")
            group_index = bound.get("groupIndex")

            if bound_type == "products":
                products = user_data.get("products", [])

                product_data = products[group_index]

                if typed_element == "image":
                    product = await get_product_data(
                        client.database,
                        product_data["name"],
                        include="info.file",
                        limit=1,
                    )

                    if product and (image_path := product.get("info", {}).get("file")):
                        image_url = f"https://assets.videoai.com.br/database/{client.niche}/{image_path}"

                        saved_change_data[element_id] = {
                            "src": image_url,
                        }

                        design.update(
                            requests.post(
                                f"{endpoint}/imageResize",
                                json=ImageResize(
                                    image=design,
                                    imageUrl=image_url,
                                    adjustment="contain",
                                ).model_dump(),
                                headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                                timeout=10,
                            )
                        )
                elif typed_element == "name":
                    design["text"] = product_data["name"]

                    saved_change_data[element_id] = {
                        "text": product_data["name"],
                    }

                    design.update(
                        requests.post(
                            f"{endpoint}/textResize",
                            json=TextResize(
                                **design,
                            ).model_dump(),
                            headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                            timeout=10,
                        )
                    )
                elif typed_element == "product-unity":
                    design["text"] = product_data.get("unity")

                    saved_change_data[element_id] = {
                        "text": product_data.get("unity"),
                    }

                    design.update(
                        requests.post(
                            f"{endpoint}/textResize",
                            json=TextResize(
                                **design,
                            ).model_dump(),
                            headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                            timeout=10,
                        )
                    )
                elif typed_element == "price":
                    split_price = re.split(
                        r"\D", str(product_data.get("price", "0,00"))
                    )

                    integer = None
                    decimal = None

                    if len(split_price) > 1:
                        integer = int(split_price[0])
                        decimal = int(split_price[1])
                    else:
                        integer = int(split_price[0])
                        decimal = 0

                    price_saved_change = {}

                    for index, item in enumerate(
                        requests.post(
                            f"{endpoint}/priceResize",
                            json=PriceResize(
                                price=design["children"],
                                integer=integer,
                                decimal=decimal,
                            ).model_dump(),
                            headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                            timeout=10,
                        )
                    ):
                        current_item = design["children"][index]

                        price_saved_change[current_item.get("id")] = item.get("text")

                        design["children"][index].update(item)

                    saved_change_data[element_id] = price_saved_change

        elif saved_data and (saved_value := saved_data.get(element_id)):
            if typed_element == "price":
                integer = None
                decimal = None

                for item in childrens:
                    item_value = int(
                        re.sub(r"\D", "", str(saved_value.get(item.get("id"), "0,00")))
                        or 0
                    )
                    _typed_element = item.get("custom", {}).get("elementType")

                    if _typed_element == "price-integer":
                        integer = item_value
                    elif _typed_element == "price-decimal":
                        decimal = item_value

                price_saved_change = {}

                for index, item in enumerate(
                    requests.post(
                        f"{endpoint}/priceResize",
                        json=PriceResize(
                            price=design["children"],
                            integer=integer,
                            decimal=decimal,
                        ).model_dump(),
                        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                        timeout=10,
                    )
                ):
                    current_item = design["children"][index]

                    price_saved_change[current_item.get("id")] = item.get("text")

                    design["children"][index].update(item)

                saved_change_data[element_id] = price_saved_change

        _childrens = []

        for _children in childrens:
            _design, saved_change_data = await process_design(
                _children,
                client,
                config,
                user_data,
                categories,
                bounds,
                saved_data=saved_data,
                saved_change_data=saved_change_data,
            )

            _childrens.append(_design)

        design["children"] = _childrens

    else:
        if element_type == "image":
            new_image = None

            if typed_element in ["client.logo-image", "client.dark-logo-image"]:
                logo = await mongo.find_one(
                    "assets_logos",
                    {
                        "owner": ObjectId(client.id),
                    }
                )

                if logo:
                    new_image = logo.get("url")

            if saved_data and (saved_value := saved_data.get(element_id)):
                new_image = saved_value.pop("src")
                design.update(saved_value)

                saved_change_data[element_id] = {
                    "src": new_image,
                }

            if new_image:
                design.update(
                    requests.post(
                        f"{endpoint}/imageResize",
                        json=ImageResize(
                            image=design,
                            imageUrl=new_image,
                            adjustment="contain",
                        ).model_dump(),
                        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                        timeout=10,
                    )
                )
        elif element_type == "text":
            has_changes = False

            if saved_data and (saved_value := saved_data.get(element_id)):
                has_changes = True
                design.update(saved_value)

            text_model = TextResize(**design).model_dump()

            if typed_element == "client.address":
                has_changes = True
                text_model.update(
                    {
                        "text": client.info.address,
                    }
                )
            elif typed_element == "client.cellphone":
                has_changes = True
                text_model.update(
                    {
                        "text": client.info.cellphone,
                    }
                )

            if saved_data and (saved_value := saved_data.get(element_id)):
                has_changes = True
                design.update(saved_value)
                text_model = TextResize(**design).model_dump()

                saved_change_data[element_id] = {
                    "text": design.get("text"),
                }

            if has_changes:
                design.update(
                    requests.post(
                        f"{endpoint}/textResize",
                        json=text_model,
                        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                        timeout=10,
                    )
                )

    if color := custom_data.get("color"):
        r, g, b, a = get_color(color, client)

        design["fill"] = f"rgba({r}, {g}, {b}, {a})"

    if user_data and categories and bound_id and bounds:
        bound = None

        if type(bounds) == dict:
            bound = bounds.get(bound_id)
        else:
            find_element = filter(lambda item: item.get("id") == bound_id, bounds)

            bound = next(find_element, {})

        bound_type = bound.get("elementType")
        group_index = bound.get("groupIndex")

        if bound_type == "products":
            products = user_data.get("products", [])

            product_data = products[group_index]

            if typed_element == "image":
                product = await get_product_data(
                    client.database, product_data["name"], include="info.file", limit=1
                )

                if product and (image_path := product.get("info", {}).get("file")):
                    image_url = f"https://assets.videoai.com.br/database/{client.niche}/{image_path}"

                    saved_change_data[element_id] = {
                        "src": image_url,
                    }

                    design.update(
                        requests.post(
                            f"{endpoint}/imageResize",
                            json=ImageResize(
                                image=design,
                                imageUrl=image_url,
                                adjustment="contain",
                            ).model_dump(),
                            headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                            timeout=10,
                        )
                    )
            elif typed_element == "name":
                design["text"] = product_data["name"]

                saved_change_data[element_id] = {
                    "text": product_data["name"],
                }

                design.update(
                    requests.post(
                        f"{endpoint}/textResize",
                        json=TextResize(
                            **design,
                        ).model_dump(),
                        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                        timeout=10,
                    )
                )
            elif typed_element == "product-unity":
                design["text"] = product_data.get("unity")

                saved_change_data[element_id] = {
                    "text": product_data.get("unity"),
                }

                design.update(
                    requests.post(
                        f"{endpoint}/textResize",
                        json=TextResize(
                            **design,
                        ).model_dump(),
                        headers={"VideoAI-Authorization": VIDEOAI_API_TOKEN},
                        timeout=10,
                    )
                )

    return design, saved_change_data