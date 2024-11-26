import json
from enum import Enum
from typing import Any, Optional

import filetype
from pydantic import BaseModel

from src.database import mongo
from src.helpers import date
from src.helpers.download import download_file
from src.helpers.exceptions import NotError
from src.helpers.gpt.speech import speech_to_text
from src.helpers.regex import array_regex, emoji_pattern, json_regex
from src.models.zapi import (
    AudioMessage,
    DocumentMessage,
    ExternalAdModel,
    ImageMessage,
    ListMessage,
    MessageTypes,
    OrderMessage,
    ProductMessage,
    ReactionMessage,
    TextMessage,
)


def extract_json(message):
    data = json_regex.search(message)

    try:
        if data:
            return json.loads(data.group(0))
    except:
        return None


def extract_array(message):
    data = array_regex.search(message)

    try:
        if data:
            return json.loads(data.group(0))
    except:
        return None


class Types(str, Enum):
    text = "text"
    image = "image"
    audio = "audio"
    order = "order"
    document = "document"
    reaction = "reaction"
    listResponseMessage = "listResponseMessage"


class MessageModel(BaseModel):
    client: str
    value: str = ""
    caption: str = ""
    type: Types = Types.text
    is_reply: bool = False
    message_id: Optional[str] = None
    reference_message_id: Optional[str] = None
    product_reference_id: Optional[str] = None
    data: Optional[Any] = None


class Message:
    @classmethod
    async def handler(cls, message: MessageTypes | dict, session):
        cls.message = TextMessage(**message) if isinstance(message, dict) else message

        cls.type = cls.get_type(cls.message)
        cls.is_reply = cls.is_reply_message(cls.message)
        cls.value = await cls.get_value(message, session)
        cls.caption = ""

        if cls.type == "image" and cls.message.image.caption:
            cls.caption = cls.message.image.caption

        if cls.type == "document" and cls.message.document.caption:
            cls.caption = cls.message.document.caption

        data = MessageModel(
            type=cls.type,
            client=cls.message.phone,
            is_reply=cls.is_reply,
            message_id=cls.message.messageId,
            reference_message_id=cls.message.referenceMessageId,
            product_reference_id=cls.message.productReferenceId,
            caption=cls.caption,
            value=cls.value,
            raw_value=cls.value,
            data=await cls.extract_data(cls.value),
        )

        if isinstance(message, ProductMessage):
            data.product_reference_id = cls.message.product.productId

        if (
            data.type == "text"
            and data.is_reply
            and (
                message_db := await mongo.database.zapi_messages.find_one(
                    {"message_id": data.reference_message_id}, {"_id": 0}
                )
            )
        ):
            message_db = MessageModel(**message_db)

            if message_db.type == "image" and message_db.caption:
                data.value = message_db.caption + "\n" + data.value
            elif message_db.type in ["text", "audio"]:
                data.value = message_db.value + "\n" + data.value

        await mongo.database.zapi_messages.insert_one(
            {**data.model_dump(), "created_at": date.now()}
        )

        return data

    @classmethod
    def is_reply_message(cls, message: MessageTypes):
        return message.referenceMessageId is not None

    @classmethod
    def get_type(cls, message: MessageTypes):
        if isinstance(message, TextMessage):
            return "text"
        elif isinstance(message, ReactionMessage):
            return "reaction"
        elif isinstance(message, ListMessage):
            return "listResponseMessage"
        elif isinstance(message, ImageMessage):
            return "image"
        elif isinstance(message, AudioMessage):
            return "audio"
        elif isinstance(message, ExternalAdModel):
            return "text"
        elif isinstance(message, OrderMessage):
            return "order"
        elif isinstance(message, DocumentMessage):
            return "document"

        return "text"

    @classmethod
    async def get_value(cls, message: MessageTypes, session):
        if cls.type == "image":
            tmp_img_path = await download_file(
                message.image.imageUrl, session.session_path
            )

            file_ext = ".png"

            file_type = filetype.guess(tmp_img_path)

            if file_type:
                file_ext = f".{file_type.extension}"

            message_value = tmp_img_path.with_suffix(file_ext).as_posix()
        elif cls.type == "audio":
            message_value = emoji_pattern.sub(
                r"", await speech_to_text(message, session)
            )
        elif cls.type == "listResponseMessage":
            message_value = emoji_pattern.sub(r"", message.listResponseMessage.title)
        elif cls.type == "order":
            message_value = message.order.products[0].name
        elif cls.type == "document":
            if not message.document.documentUrl:
                raise Exception("Document url doents exists")

            if message.document.mimeType not in ("image/png"):
                session.zapi.send_text(
                    "A resposta enviada não é válida 😓, somente aceitamos texto, imagens e áudio!"
                )

                raise NotError()

            tmp_img_path = await download_file(
                message.document.documentUrl, session.session_path
            )

            message_value = tmp_img_path.with_suffix(".png").as_posix()
        else:
            message_value = emoji_pattern.sub(r"", message.text.message)

        return message_value

    @classmethod
    async def extract_data(cls, message: str):
        data = json_regex.search(message)

        if data:
            return json.loads(data.group(0))
