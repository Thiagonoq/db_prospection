from datetime import datetime
import json
from copy import deepcopy
import logging
from pathlib import Path
from bson import ObjectId
import requests

import config
from src.api.request import Requests
from src.database.mongo import mongo
from src.handlers.client import Client
from src.routes.template import process_design


async def create_template(prospect_client_id: ObjectId):
    template_id = config.BF_TEMPLATE
    
    cached_objects = {}

    try:
        cached_objects = json.loads(Path("cached_objects.json").read_text())
    except:
        pass

    try:
        print("Get saved changes list")

        main_saved_changes = await mongo.find_one("saved_changes", {"client": prospect_client_id, "template_id": ObjectId(template_id)})

        print("Get templates")

        templates = await mongo.find(
            "templates",
            {
                "designs.design": {"$exists": True}
            }
        )

        if not templates:
            raise Exception("No templates found") 

        templates = {str(template["_id"]): template for template in templates}

        print("Get clients")


        try:
            client = await Client.init(str(prospect_client_id), pre_register=False)
        except Exception as e:
            logging.exception(e)

            with open("error.txt", "a") as f:
                f.write(f"Client {str(prospect_client_id)}\n")

        print(f"Client {client.id} started")

        try:
            saved_changes = deepcopy(main_saved_changes)
            saved_changes["client_id"] = str(prospect_client_id)

            template = templates.get(str(saved_changes.get("template_id")))

            if not template:
                raise Exception("Template not found.")

            _config = await mongo.get_config()

            design_data = template.get("designs")

            if not design_data:
                raise Exception("Design not found.")

            question = design_data.get("question")
            design_model = design_data.get("design")

            if not design_model:
                raise Exception("Design options not found.")

            design_content = Requests().get(design_model)

            design_custom = design_content.get("custom", {})
            design = design_content.get("design", {})

            question_value = saved_changes.get("project_data", {}).get(
                "questionValue", 1
            )

            if question and question_value != None:
                question_type = question.get("type")

                design_custom = design["pages"][0].get("custom", {})

                bounds = design_custom.get("bounds", {})
                item_variations = design_custom.get("itemVariation", {})

                if question_type == "product_quantity":
                    bound_ids = set(
                        [
                            element_id
                            for row in map(
                                lambda item: [
                                    *item.get("children", []),
                                    *item.get("types", {}).values(),
                                ],
                                bounds.values(),
                            )
                            for element_id in row
                        ]
                    )

                    design["pages"][0]["children"] = [
                        children
                        for children in design["pages"][0]["children"]
                        if children.get("id") not in bound_ids
                    ]

                    products = item_variations.get("products", {}).get(
                        str(question_value), {}
                    )

                    if not products:
                        products = item_variations.get("products", {}).get(
                            "1", {}
                        )

                    design["pages"][0]["children"].extend(
                        products.get("children", [])
                    )
                    design["pages"][0]["custom"]["bounds"] = products.get(
                        "bounds", {}
                    )

            for _page in design["pages"]:
                for index, _element in enumerate(_page.get("children", [])):
                    _element_id = _element.get("id")
                    _custom_data = _element.get("custom", {})
                    _typed_element = _custom_data.get("elementType")

                    if (
                        not str(_typed_element).startswith("client")
                        and saved_changes["data"].get(_element_id)
                        and (
                            cached_object := cached_objects.get(
                                str(template["_id"]), {}
                            ).get(_element_id)
                        )
                    ):
                        _page["children"][index] = cached_object
                        del saved_changes["data"][_element_id]
                        continue

            design = (
                await process_design(
                    design,
                    client,
                    _config,
                    saved_data=saved_changes["data"],
                )
            )[0]

            for _page in design["pages"]:
                for _element in _page.get("children", []):
                    _element_id = _element.get("id")
                    _custom_data = _element.get("custom", {})
                    _typed_element = _custom_data.get("elementType")

                    if not str(_typed_element).startswith("client"):
                        if str(template["_id"]) not in cached_objects:
                            cached_objects[str(template["_id"])] = {}

                        if _element_id in cached_objects[str(template["_id"])]:
                            continue

                        cached_objects[str(template["_id"])][_element_id] = (
                            deepcopy(_element)
                        )

                        print(f"Element {str(_element_id)} cached")

            insert_saved_changes = {
                "type": "art",
                "template_id": template["_id"],
                "client": ObjectId(client.id),
                "project_data": saved_changes.get("project_data", {}),
                "data": saved_changes["data"],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "generated": True,
            }

            saved_changes_id = await mongo.insert_one(
                "saved_changes",
                insert_saved_changes
            )

            saved_changes_id = str(saved_changes_id.inserted_id)

            response = requests.post(
                "https://api.art.v2.videoai.com.br",
                json={
                    "design": design,
                    "replace": False,
                    "data": {},
                    "metadata": {
                        "templateId": template_id,
                        "savedChangesId": str(saved_changes_id),
                        "clientId": str(prospect_client_id)
                    },
                    "webhook": "https://fond-greatly-spider.ngrok-free.app/response",
                },
                headers={
                    "VideoAI-Authorization": config.VIDEOAI_API_TOKEN,
                },
            )

            if response.status_code != 200:
                logging.error(response.text)
                raise Exception("Error on creating template")

        except Exception as e:
            logging.exception(e)

            with open("error.txt", "a") as f:
                f.write(
                    f"Client {prospect_client_id} - Saved changes {1}\n"
                )

        print(f"Client {client.id} finished")

    except Exception as e:
        logging.exception(e)

        with open("error.txt", "a") as f:
            f.write(f"Client {prospect_client_id}\n")

    finally:
        Path("cached_objects.json").write_text(json.dumps(cached_objects))
    

    return response
