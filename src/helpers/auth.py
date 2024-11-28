from datetime import datetime
import logging
import uuid
from bson import ObjectId

from src.database.mongo import mongo
import config

async def create_login_url(client_id: ObjectId, pass_by_client_id: str = None):
    easy_login = uuid.uuid4().hex

    client = await mongo.find_one("clients", {"_id": client_id})

    pass_by_client = None

    if not client:
        logging.error(f"Client not found: {client_id}")
        return None
    
    data = {
        "client": client_id,
        "easy_login": easy_login,
        "createdAt": datetime.now(),
    }

    if client.get("is_dev"):
        if pass_by_client_id:
            pass_by_client = await mongo.find_one(
                "clients", {"_id": ObjectId(pass_by_client_id), "is_dev": False}
            )

            if pass_by_client:
                data["pass_by_client"] = ObjectId(pass_by_client_id)
            else:
                logging.error(f"Client not found: {pass_by_client_id}")
                return None

    index_info = await mongo.index_information("easy_login")

    if "createdAt_1" not in index_info:
        try:
            await mongo.get_collection("easy_login").create_index(
                "createdAt", expireAfterSeconds=60 * 60 * 24 * 2
            )
        except:
            pass

    username = client.get("username")
    password = client.get("password")

    await mongo.insert_one("easy_login", data)

    route = (
        f"login/{easy_login}"
        if username and password
        else f"registrar/{client['niche']}/{easy_login}"
    )

    return f"https://app.videoai.com.br/{route}?redirect=/biblioteca"