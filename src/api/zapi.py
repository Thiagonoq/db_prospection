import base64
import logging
import mimetypes
import re
from pathlib import Path

import requests

from config import DEV, ZAPI_CLIENT_TOKEN, ZAPI_ENDPOINT
from src.helpers.is_ import Is
from src.helpers.regex import (
    array_regex,
    file_replace_regex,
    json_replace_regex,
    questions_actions_regex,
    questions_type_regex,
)


class ZApi:

    def __init__(
        self,
        phones: str | list = None,
        parser: bool = True,
        zapi_endpoint: str = ZAPI_ENDPOINT,
    ):
        self.phones = phones
        self.parser = parser
        self.zapi_endpoint = zapi_endpoint

    def _make_request(self, path, phone, body):
        try:
            return requests.post(
                self.zapi_endpoint + path,
                json={"phone": phone, **body},
                headers={"Client-Token": ZAPI_CLIENT_TOKEN},
            ).json()
        except Exception as e:
            logging.exception(e)

        return False

    def _post(self, path: str, body: dict):
        if type(self.phones) == str:
            return self._make_request(path, self.phones, body)

        response = {}

        for phone in self.phones:
            response[phone] = self._make_request(path, phone, body)

        return response

    def _get(self, path: str):
        try:
            return requests.get(
                self.zapi_endpoint + path, headers={"Client-Token": ZAPI_CLIENT_TOKEN}
            ).json()
        except Exception as e:
            logging.exception(e)

        return False

    def _put(self, path: str, **kwargs):
        try:
            return requests.put(
                self.zapi_endpoint + path,
                **kwargs,
                headers={"Client-Token": ZAPI_CLIENT_TOKEN},
            ).json()
        except Exception as e:
            logging.exception(e)

        return False

    def _parse_file(self, file: str | bytes | Path):
        if isinstance(file, Path):
            with open(file, "rb") as f:
                return base64.b64encode(f.read()).decode()
        elif isinstance(file, bytes):
            return base64.b64encode(file).decode()
        elif Is.url(file):
            return base64.b64encode(requests.get(file).content).decode()

        return file

    def send_text(self, message: str, parser: bool = True):
        return self._post("/send-text", {"message": self._parse_text(message, parser)})

    def send_image(self, image: str | bytes | Path, caption: str = ""):
        return self._post(
            "/send-image",
            {
                "image": "data:image/png;base64," + self._parse_file(image),
                "caption": caption,
            },
        )

    def send_sticker(self, sticker: str | bytes | Path):
        return self._post(
            "/send-sticker",
            {"sticker": "data:image/png;base64," + self._parse_file(sticker)},
        )

    def send_audio(self, audio: str | bytes | Path):
        return self._post(
            "/send-audio",
            {"audio": "data:audio/mp3;base64," + self._parse_file(audio)},
        )

    def send_list(self, message: str, option_list: dict):
        return self._post(
            "/send-option-list",
            {"message": message, "optionList": option_list},
        )

    def send_video(self, video: str | bytes | Path, caption: str = ""):
        return self._post(
            "/send-video",
            {
                "video": "data:video/mp4;base64," + self._parse_file(video),
                "caption": caption,
            },
        )

    def send_document(
        self,
        document: str | bytes | Path,
        file_name: str,
        mime_type: str,
        extension: str,
        caption: str = "",
    ):
        return self._post(
            f"/send-document/{extension}",
            {
                "caption": caption,
                "fileName": file_name,
                "document": f"data:{mime_type};base64," + self._parse_file(document),
            },
        )

    def send_contact(self, contact_name: str, contact_phone: str):
        return self._post(
            "/send-contact",
            {"contactName": contact_name, "contactPhone": contact_phone},
        )

    def send_catalog(self):
        return self._post("/send-catalog", {"catalogPhone": "553597585415"})

    def update_webhook_received(self, url: str):
        return self._put("/update-webhook-received", json={"value": url})

    def get_product_by_id(self, product_id: str):
        return self._get(f"/products/{product_id}")

    def read_chat(self, action: str = "read"):
        return self._post("/modify-chat", {"action": action})

    def get_chats(self, page: int = 1, page_size: int = 100):
        return self._get(f"/chats?page={page}&pageSize={page_size}")

    def get_tags(self):
        return self._get("/tags")

    def add_tag(self, phone: str, tag: str):
        return self._put(f"/chats/{phone}/tags/{tag}/add")

    def remove_tag(self, phone: str, tag: str):
        return self._put(f"/chats/{phone}/tags/{tag}/remove")

    def get_profile_metadata(self, phone: str):
        return self._get(f"/contacts/{phone}")

    def get_profile_picture(self, phone: str):
        return self._get(f"/profile-picture?phone={phone}")

    def check_phone_exists(self, phone: str):
        return self._get(f"/phone-exists/{phone}")

    def _parse_text(self, text: str, parser: bool = True):
        if DEV or not parser:
            return text

        if not self.parser:
            return

        text = re.sub(file_replace_regex, "", text)
        text = re.sub(json_replace_regex, "", text)
        text = re.sub(questions_actions_regex, "", text)
        text = re.sub(questions_type_regex, "", text)
        text = re.sub(array_regex, "", text)

        if "JSON" in text:
            text = "Erro"

        return text
