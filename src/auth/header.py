from argon2 import PasswordHasher
from fastapi import Header, HTTPException

import config
from src.database import mongo


async def get_token_header(
    token: str = Header(alias="VideoAI-Authorization", default="")
):
    if token != config.VIDEOAI_API_TOKEN:
        raise HTTPException(status_code=400)


class GetTokenChecker:
    def __init__(self, name: str):
        self.name = name

    async def __call__(
        self, token: str = Header(alias="VideoAI-Authorization", default="")
    ):
        try:
            if PasswordHasher().verify(
                (await mongo.get_config()).get(f"{self.name}_token"), token
            ):
                return token
        except:
            pass

        raise HTTPException(status_code=404)
