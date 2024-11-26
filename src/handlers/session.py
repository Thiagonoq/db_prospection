import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import config
from src.api.zapi import ZApi
from src.database import mongo
from src.handlers.client import Client
from src.helpers.analytics import Analytics
from src.helpers.async_object import AsyncObject
from src.helpers.exceptions import NotError
from src.helpers.flow import Flow
from src.helpers.message import Message, MessageModel
from src.models.analytics import TemplateAnalytics
from src.models.zapi import MessageTypes


class Session(AsyncObject):
    message: MessageModel
    flow: Flow
    client: Client
    analytics: Analytics
    config: dict

    async def __init__(
        self,
        message: MessageTypes = None,
        ignore_lock: bool = True,
        flow_id: str = None,
        **kwargs,
    ):
        self._message = message
        self.phone = message.phone if message else kwargs.get("phone")
        self.now = datetime.now()

        self.config = await mongo.get_config()

        self.client = await Client.init(self.phone, session_config=self.config)

        self.client.last_activity = self.now

        logging.info(f"Session started for {self.phone}")

        await self.client.save()

        self.flow = await Flow.init(self.phone, flow_id=flow_id)

        logging.info(f"Flow started for {self.phone}")

        if not ignore_lock and self.flow.lockCreation:
            raise NotError()

        self.valid = not message or await self.check(message)

        logging.info(f"Session valid for {self.phone}: {self.valid}")

        if not self.valid:
            return None

        await self._start_timeout()

        self.session_path: Path = config.TMP_PATH / self.phone / self.flow.id
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.analytics = await Analytics.init(self.phone)

        if not self.flow.startedFlow:
            self.flow.startedFlow = datetime.now()

        self.zapi = ZApi(self.phone)

    async def _start_timeout(self):
        await mongo.database.timeout.update_one(
            {"client": self.phone},
            {"$set": {"datetime": self.now + timedelta(minutes=10)}},
            upsert=True,
        )

    async def _end_timeout(self):
        await mongo.database.timeout.delete_one({"client": self.phone})

    async def init(self):
        self.message = await Message.handler(self._message, self)

        template_name = self.flow.currentTemplate

        if not self.flow.currentTemplate:
            template_name = "NotIdentified"

        if template_name not in [
            template.name for template in self.analytics.templates
        ]:
            new_template_analytics = TemplateAnalytics(name=template_name)

            if self.message.type == "image":
                new_template_analytics.sended.image += 1
            elif self.message.type == "audio":
                new_template_analytics.sended.audio += 1
            else:
                new_template_analytics.sended.text += 1

            self.analytics.templates.append(new_template_analytics)
        else:
            for template in self.analytics.templates:
                if template.name == template_name:
                    if self.message.type == "image":
                        template.sended.image += 1
                    elif self.message.type == "audio":
                        template.sended.audio += 1
                    else:
                        template.sended.text += 1

                    break

        await self.analytics.save()

    async def check(self, message: MessageTypes):
        message_id = message.messageId

        if message.isGroup:
            return False

        if message_id in self.flow.messageIds and not message.isEdit:
            return False

        self.flow.messageIds.append(message_id)

        return True

    async def end(self, remove_path: bool = True, error: bool = False):
        if remove_path and not config.DEV and self.session_path.exists():
            shutil.rmtree(self.session_path)
            self.session_path.unlink(missing_ok=True)

        await self.move_threads(error)

        await self.flow.reset()
        await self._end_timeout()

    async def move_threads(self, error: bool = False):
        await mongo.move_to_another(
            {"id": self.flow.thread}, {"error": error}, "threads", "old_threads"
        )

        if self.flow.subThreads:
            for sub_thread in self.flow.subThreads:
                await mongo.move_to_another(
                    {"id": sub_thread},
                    {"error": error},
                    "threads",
                    "old_threads",
                )
