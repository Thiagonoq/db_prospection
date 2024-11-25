import asyncio
import random
from argon2 import PasswordHasher

from bson import ObjectId

from src.helpers.auth import create_login_url
from src.database.mongo import mongo
from src.helpers.make_template import create_template
import config


async def create_link():
    try:
        print(await create_login_url(ObjectId("65c3930227b3107414c18364")))

    except Exception as e:
        print(f"Erro geral: {e}")

async def generate_login():
    try:
        clients = await mongo.find(
            "clients", 
            {
                "niche": "hortifruti",
                "registered": True,
                "purchase.type": {
                    "$nin": ["paid"]
                },
            }
        )

        for client in clients:
            username = client.get("username")
            password = client.get("password")

            if not username and not password:
                username = client.get("main_client")
                password = PasswordHasher().hash(str(random.randint(100000, 999999)))

                await mongo.update_one(
                    "clients",
                    {"_id": client.get("_id")},
                    {
                        "$set": {
                            "username": username,
                            "password": password,
                        }
                    }
                )

                print(f"Login criado para {username} com senha {password}")

    except Exception as e:
        print(f"Erro geral: {e}")

async def test_art_generation():
    response = await create_template(ObjectId("65f35246a5c0f95aaad79e1f"))
    print(response)

if __name__ == "__main__":
    try:
        # asyncio.run(generate_login())
        # asyncio.run(create_link())
        asyncio.run(test_art_generation())

    except Exception as e:
        print(f"Erro geral: {e}")