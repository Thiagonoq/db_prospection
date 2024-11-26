import asyncio
import logging
from pathlib import Path

import requests

import config
from src.api.zapi import ZApi
from src.helpers import audio


class ElevenLabs:
    def __init__(self):
        self.feminine_voice()

    async def generate(self, audio_path: str | Path, text: str):
        trys = 2

        while trys != 0:
            try:
                response = requests.post(
                    f"{config.ELEVENLABS_API_URL}/{self.voice_id}",
                    json={
                        "model_id": "eleven_multilingual_v1",
                        "text": text,
                        "voice_settings": {"stability": 1, "similarity_boost": 1},
                        "generation_config": {
                            "chunk_length_schedule": [500, 500, 500, 500]
                        },
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Xi-Api-Key": config.ELEVENLABS_API_KEY,
                    },
                )

                if not response.content:
                    continue

                audio_path.write_bytes(response.content)

                if not audio.is_valid(audio_path):
                    continue

                return audio.normalize(audio_path)
            except Exception as e:
                logging.exception(e)
            finally:
                trys -= 1
                await asyncio.sleep(5)

        raise Exception("ElevenLabs failed to generate!")

    def male_voice(self):
        self.voice_id = "bVMeCyTHy58xNoL34h3p"

    def feminine_voice(self):
        self.voice_id = "jsCqWAovK2LkecY7zXl4"
