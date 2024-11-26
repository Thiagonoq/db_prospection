import logging
import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import rembg
import requests
from PIL import Image as PILImage
from webptools import cwebp

import config
from src.helpers.is_ import Is


class Picwish:
    def __init__(self, client=None):
        self.url = os.getenv("PICWISH_API_URL")

    def _get_file(self, image: str | BinaryIO):
        if Is.url(image):
            with requests.get(image, stream=True) as response:
                return BytesIO(response.content)
        elif (type(image) == str or isinstance(image, Path)) and (path := Path(image)):
            return open(image, "rb")
        else:
            return image

    def _request(self, url, headers, data, files):
        trys = 3

        while trys > 0:
            try:
                logging.info(
                    f"Trying to remove the background from the image. {trys} attempts left. {url}"
                )
                return requests.post(
                    url, headers=headers, data=data, files=files, timeout=60
                )
            except Exception as e:
                logging.error(f"picwish: {e}")
                trys -= 1

        raise Exception("Não foi possível remover o fundo da imagem.")

    def _request_image(self, image):
        file = self._get_file(image)
        headers = {"X-API-KEY": os.getenv("PICWISH_API_KEY")}
        data = {"sync": "1", "crop": "1"}
        files = {"image_file": file}

        response = self._request(self.url, headers, data, files)

        if response.status_code != 200:
            logging.error(f"picwish: {response.text}")
            raise Exception("Não foi possível remover o fundo da imagem.")

        response = response.json()

        logging.info(f"picwish: {response}")

        if response.get("status") != 200 and response.get("message") != "success":
            raise Exception("Não foi possível remover o fundo da imagem.")

        image = response.get("data", {}).get("image", "")

        logging.info(f"picwish: {image}")

        if not image:
            raise Exception("Não foi possível remover o fundo da imagem.")

        return image

    def resize_image_proportional(
        self, image: PILImage, output_path, max_width, max_height
    ):
        if image.width > max_width or image.height > max_height:
            aspect_ratio = image.width / image.height

            if aspect_ratio > 1:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)

            logging.info(f"picwish: {image} (resizing)")

            image = image.resize((new_width, new_height))

            image.save(output_path)

    def process_image(self, image):
        image_data = PILImage.open(self._get_file(image)).convert("RGBA")

        if image_data.getextrema()[-1] != (
            255,
            255,
        ):
            return image

        self.resize_image_proportional(image_data, image, 4096, 4096)

        if os.path.getsize(image) > 15 * 1024 * 1024:
            logging.info(f"picwish: {image} (compressing)")

            image_path = Path(image)
            image = image_path.with_suffix(".webp").as_posix()

            cwebp(
                input_image=image_path.as_posix(),
                output_image=image,
                option="-q 90",
            )

        try:
            process_image = self._request_image(image)
        except Exception as e:
            logging.error(f"picwish: {e}")

            process_image = config.TMP_PATH / (uuid.uuid4().hex + ".png")

            rembg.remove(image_data).save(process_image)

            image = PILImage.open(process_image).convert("RGBA")

            image = image.resize(image.getbbox())

            image.save(process_image)

        return process_image
