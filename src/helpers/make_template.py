import json
import logging
from bson import ObjectId
import requests

import config
from src.database.mongo import mongo


async def create_template(prospect_client_id: ObjectId):
    with open("template.json", "r", encoding="utf-8") as f:
        template_data = json.load(f)

    template_id = config.BF_TEMPLATE
    prospect_template = await mongo.find_one("saved_changes", {"client": prospect_client_id, "template_id": ObjectId(template_id)})

    saved_changes_id = prospect_template.get("_id", "")


    design = template_data.get("design", {})
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
    

    return response
