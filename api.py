import json
import logging
import os
import base64
import uuid
import aiohttp
from bson import ObjectId
from fastapi import FastAPI, Request, HTTPException

import config
from utils.zapi import Zapi
from src.database.mongo import mongo
from src.api.firebase import initialize_firebase, send_to_firebase

zapi_credentials = config.ZAPI_CREDENTIALS["Stênio"]["primary"]

zapi_instance = zapi_credentials[0]
zapi_token = zapi_credentials[1]

zapi_client_token = config.ZAPI_CLIENT_TOKEN

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Olá, Mundo!"}

@app.post("/response")
async def handle_response(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    image_base64 = data.get("file")
    if not image_base64:
        raise HTTPException(status_code=400, detail="Campo 'file' ausente no JSON")

    try:
        image_data = base64.b64decode(image_base64)
        temp_path = config.TMP_PATH / f"image_{uuid.uuid4()}.png"
        #save image to temp folder
        with open(temp_path, "wb") as f:
            f.write(image_data)

        initialize_firebase()
        client_id = data.get("metadata", {}).get("clientId")
        logging.info(f"Client ID: {client_id}")
        image_url = send_to_firebase(temp_path, client_id)

        client = await mongo.find_one(
            "clients", {"_id": ObjectId(client_id)}
        )
        logging.info(f"Client: {client}")
        client_phones = client.get("client", [])
        updated = False
        for phone in client_phones:
            prospect_data = await mongo.find_one(
                "prospecting_BF",
                {
                    "phone": phone,
                }
            )
            if prospect_data:
                await mongo.update_many(
                    "prospecting_BF",
                    {
                        "phone": phone
                    },
                    {
                        "$set": {
                            "image.url": image_url
                        }
                    }
                )
                updated = True
        
        if not updated:
            logging.warning(f"Telefone {phone} nao encontrado no banco de dados")
            logging.warning(f"Url: {image_url}")
            return {"status": "sucesso", "filename": temp_path}
        
        temp_path.unlink()

    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="String Base64 inválida")

    return {"status": "sucesso", "filename": temp_path}
