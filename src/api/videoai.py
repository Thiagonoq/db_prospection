from datetime import datetime
import logging
import random
from http.client import HTTPException

import requests

import config
from src.database import mongo


def post_data(url: str, data, headers):
    try:
        logging.info(f"Sending request to {url} with data: {data}")

        response = requests.post(url, json=data, headers=headers, timeout=10)

        if response.status_code != 200:
            raise Exception(f'Request failed with status code "{response.status_code}"')
        return response.json()
    except Exception as e:
        logging.error(f"Failed to send request to {url}: {e}")
        return None


async def router_post(routes, data, priority: int = 2, headers: dict = {}):
    routes_length = len(routes)

    if routes_length == 0:
        raise HTTPException(status_code=401, detail="No routes available")

    while routes:
        selected_route_index = random.choice([i for i in range(len(routes))])
        url = f"{routes[selected_route_index]}?priority={priority}"

        response = post_data(url, data, headers)

        if response:
            return response
        else:
            routes.pop(selected_route_index)
            logging.error(f"Failed to send request to {routes[selected_route_index]}")

    logging.error("Failed to send request to all routes")

    raise HTTPException(status_code=401, detail="Failed to send request to all routes")


class VideoAIServices:
    def __init__(self, phone: str, session_config: dict = {}):
        self.phone = phone
        self.session_config = session_config

    async def _logging_post_data(self, data: dict, type: str):
        await mongo.database.logging_post_data.insert_one(
            {
                "type": type,
                "phone": self.phone,
                "session_config": self.session_config,
                "data": data,
                "date": datetime.now(),
            }
        )

    async def video(self, data: dict):
        await self._logging_post_data(data, "video")

        endpoint = self.session_config.get("api_video_endpoint")

        if not endpoint:
            raise Exception("Endpoint de vídeo não encontrado no config!")

        response = requests.post(
            endpoint,
            json=data,
            headers={
                "X-Media-Type": "video",
                "VideoAI-Authorization": config.VIDEOAI_API_TOKEN,
            },
            verify=False,
        )

        if response.status_code != 200:
            raise Exception(
                f"Um erro ocorreu na api de vídeo!\nHTTP Status: {response.status_code}\nEndpoint: {endpoint}\n\nBody:\n{response.text}"
            )

        return response

    async def image(
        self,
        client: str,
        template: str,
        webhook: str,
        data: dict,
        database: dict = {},
        is_sticker: bool = False,
        priority: int = 9,
    ):
        post_data = {
            "data": data,
            "client": client[0] if isinstance(client, list) else client,
            "template": template,
            "webhook": webhook,
            "sticker": is_sticker,
            "database": database,
        }

        await self._logging_post_data(post_data, "image")

        response = requests.post(
            f"http://0.0.0.0:8001?priority={priority}",
            json=post_data,
            headers={
                "VideoAI-Authorization": config.VIDEOAI_API_TOKEN,
                "X-Media-Type": "art",
            },
        )

        if response.status_code != 200:
            raise Exception(
                f"Um erro ocorreu na api de imagem!\nHTTP Status: {response.status_code}\nBody:\n{response.text}"
            )

        return response

    async def image_pack(
        self,
        client: str,
        webhook: str,
        jobs: list,
        affiliate: str = False,
        is_paid: bool = False,
        session_id: str = "",
        priority: int = 9,
        metadata: dict = {},
    ):
        post_data = {
            "jobs": jobs,
            "client": client[0] if isinstance(client, list) else client,
            "webhook": webhook,
            "affiliate": affiliate,
            "isPaid": is_paid,
            "sessionId": session_id,
            "metadata": metadata,
        }

        await self._logging_post_data(post_data, "image_pack")

        response = requests.post(
            f"http://0.0.0.0:8001?priority={priority}",
            json=post_data,
            headers={
                "VideoAI-Authorization": config.VIDEOAI_API_TOKEN,
                "X-Media-Type": "art",
            },
        )

        if response.status_code != 200:
            raise Exception(
                f"Um erro ocorreu na api de imagem!\nHTTP Status: {response.status_code}\nBody:\n{response.text}"
            )

        return response
