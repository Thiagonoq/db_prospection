from datetime import datetime

from src.database import mongo
from src.helpers import date
from src.models.analytics import (
    GPT,
    AnalyticsModel,
    BaseUsage,
    FlowAnalytics,
    GPTTextModel,
    GPTWhisperModel,
    SendedMessages,
    TemplateAnalytics,
    Usage,
)


class Analytics(AnalyticsModel):
    _now: datetime

    @classmethod
    async def init(cls, client: str, **kwargs):
        instance = cls(client=client, **kwargs)

        now = date.now()

        instance._now = datetime(now.year, now.month, now.day)

        await instance.get()

        return instance

    async def get(self):

        data = await mongo.database.analytics.find_one(
            {
                "client": self.client,
                "created_at": {"$gte": self._now},
            },
            {"_id": 0},
        )

        if data:
            self.__update_internal(data)
        else:
            return await self.create()

        return self

    async def create(self):
        data = self.model_dump()

        data["created_at"] = date.now()

        await mongo.database.analytics.insert_one(data)
        self.__update_internal(data)

        return self

    async def save(self):
        data = self.model_dump()

        data["updated_at"] = date.now()

        await mongo.database.analytics.update_one(
            {"client": self.client, "created_at": {"$gte": self._now}},
            {"$set": data},
        )

    def dump(self, **kwargs):
        data = self.model_dump()

        if kwargs:
            data.update({**kwargs})
            data = AnalyticsModel(**data).model_dump()

        return data

    def __update_internal(self, data: dict):
        self.__dict__.update(
            {
                "client": data["client"],
                "templates": [
                    TemplateAnalytics(
                        name=template["name"],
                        published=template["published"],
                        requestedCatalog=template["requestedCatalog"],
                        sended=SendedMessages(**template["sended"]),
                        usage=Usage(
                            created=BaseUsage(**template["usage"]["created"]),
                            edited=BaseUsage(**template["usage"]["edited"]),
                        ),
                        gpt=GPT(
                            usage=[
                                (
                                    GPTTextModel(**model)
                                    if "seconds" not in model
                                    else GPTWhisperModel(**model)
                                )
                                for model in template["gpt"]["usage"]
                            ],
                        ),
                        flows=[FlowAnalytics(**flow) for flow in template["flows"]],
                    )
                    for template in data["templates"]
                ],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
            }
        )
