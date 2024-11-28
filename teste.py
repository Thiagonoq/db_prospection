import asyncio
import json
import random
from argon2 import PasswordHasher
import requests

from bson import ObjectId

from src.helpers.auth import create_login_url
from src.database.mongo import mongo
from src.helpers.make_template import create_template
import config


async def create_link():
    try:
        print(await create_login_url(ObjectId("65dc90581318411f4bec7933")))

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
    response = await create_template(ObjectId("665f169147ee179c0954145a"))
    print(response)


async def create_frozen_db():
    phones= [
        "558896450488",
        "5521970244398",
        "5519991452295",
        "5511998094463",
        "559186269508",
        "559185681201",
        "5528999095598",
        "557791818170",
        "556194262900",
        "553187169057",
        "5527996288905",
        "559888850007",
        "559182134116",
        "558183675942",
        "554192644282",
        "559291045852",
        "555192542896",
        "5521998754551",
        "5527988568257",
        "5528999663328",
        "5513988684994",
        "556285637044",
        "5527998753449",
        "556198098341",
        "5522981621399",
        "551995373269",
        "5511987429306",
        "553597375563",
        "5511991908922",
        "5511980853886",
        "558491317423",
        "553898837295",
        "559292784065",
        "556696479571",
        "558594473600",
        "558592700865",
        "5518996592398",
        "552298930032",
        "556295748336",
        "559292417006",
        "556296131706",
        "554197287378",
        "557183834976",
        "557998477682",
        "557381696602",
        "553598838239",
        "5522998822718",
        "553187111070",
        "558299407129",
        "557488580742",
        "5522981643553",
        "553291679139",
        "555391629068",
        "559888149532",
        "559191818985",
        "554384210646",
        "5519974099161",
        "5511985208353",
        "559292105184",
        "557185021205",
        "559284617037",
        "5511947463202",
        "552164219524",
        "557481035758",
        "559996492636",
        "559185818128",
        "557193788342",
        "558296733889",
        "559884469605",
        "559991104724",
        "553195277570",
        "557792037093",
        "554491671148",
        "5521965654700",
    ]

    frozen_data = []
    for phone in phones:
        client_data = await mongo.find_one("clients", {"client": phone})

        if not client_data:
            print(f"Cliente {phone} nao encontrado")
            continue

        client = {
            "phone": phone,
            "prospector": client_data.get("prospector", {}).get("name").replace(" - Video AI", ""),
        }

        frozen_data.append(client)

    with open("frozen_db.json", "w", encoding="utf-8") as f:
        json.dump(frozen_data, f, indent=4)


async def get_links():
    saved_changes = await mongo.find_one(
            "saved_changes",
            {
                "client": ObjectId("65c5254bab7a00ee07fdb31e"),
                "template_id": ObjectId("6605bd3534db70ef71a34409")
            }
        )
    image_thumb = saved_changes.get("thumbnail", "")
    image_url = image_thumb.replace("_500x500.webp", ".png")

    try:
        #tenta validar se existe a imagem no link
        response = requests.get(image_url)
        if response.status_code == 200:
            print("Imagem encontrada no link:", image_url)
        else:
            print("Imagem nao encontrada no link:", image_url)

    except Exception as e:
        print("Erro ao validar a imagem no link:", image_url, e)

if __name__ == "__main__":
    try:
        # asyncio.run(generate_login())
        # asyncio.run(create_link())
        asyncio.run(get_links())
        # asyncio.run(test_art_generation())
        # asyncio.run(create_frozen_db())

    except Exception as e:
        print(f"Erro geral: {e}")