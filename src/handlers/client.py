from bson import ObjectId

import config

from src.database.mongo import mongo

from src.helpers.pathobject import PathsObject
from src.models.client import (
    CRM,
    ClientAnalytics,
    ClientInfoModel,
    ClientModel,
    ClientPreferences,
    Colors,
    Cta,
    Narration,
    Prospector,
    Purchase,
)


class Client(ClientModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._exists: bool
        self._paths: PathsObject
        self._get_by_username: bool
        self._get_by_id: bool
        self._templates: list
        self._session_config: dict
        self._client: str

    @classmethod
    async def init(
        cls,
        client: str = None,
        username: str = None,
        get_by_username: bool = False,
        session_config: dict = {},
        pre_register: bool = True,
        **kwargs,
    ) -> "Client":
        instance = cls(client=client, username=username, **kwargs)

        instance._exists = False
        instance._get_by_username = get_by_username
        instance._session_config = session_config
        instance._client = client

        await instance.__load(pre_register)

        if client and pre_register:
            images_path = config.CLIENTS_PATH / f"images/{instance.main_client}"
            audios_path = config.CLIENTS_PATH / f"audios/{instance.main_client}"

            images_path.mkdir(parents=True, exist_ok=True)
            audios_path.mkdir(parents=True, exist_ok=True)

            instance._paths = PathsObject(images=images_path, audios=audios_path)

        return instance

    async def __load(self, pre_register: bool = True):
        query = {}

        _id = None

        try:
            _id = ObjectId(self.client)
        except:
            pass

        if _id:
            query = {"_id": _id}
        else:
            query = {"client": self.client}

            if self._get_by_username:
                query = {"$or": [{"username": self.username}, query]}
        
        client = await mongo.find_one("clients", query) or {}

        self._exists = not (not client) and (client.get("registered") or False)

        if not client and pre_register:
            await self.pre_register()
            return

        self._client = client.get("main_client") or self.client or self._client

        self.__dict__.update(
            {
                "id": str(client.get("_id")),
                "client": client.get("client"),
                "main_client": self._client,
                "username": client.get("username"),
                "password": client.get("password"),
                "niche": client.get("niche"),
                "database": client.get("database"),
                "info": ClientInfoModel(**(client.get("info") or {})),
                "options": client.get("options"),
                "templates": client.get("templates", []),
                "images": client.get("images", []),
                "created_at": client.get("created_at"),
                "purchase": Purchase(**client.get("purchase", {}) or {}),
                "analytics": ClientAnalytics(**client.get("analytics", {})),
                "preferences": ClientPreferences(**client.get("preferences", {})),
                "narration": Narration(**client.get("narration", {}) or {}),
                "is_dev": client.get("is_dev"),
                "has_logo": client.get("has_logo", False),
                "has_profile_logo": client.get("has_profile_logo", False),
                "logo_by_designer": client.get("logo_by_designer", False),
                "prospector": Prospector(**client.get("prospector", {})),
                "cta": Cta(**client.get("cta", {})),
                "crm": CRM(**client.get("crm", {}) or {}),
                "registered": client.get("registered", False),
                "is_tutorial": client.get("is_tutorial", True),
                "flow_state": client.get("flow_state"),
                "colors": Colors(**client.get("colors", {}) or {}),
                "synced": client.get("synced", False),
            }
        )

        template_ids = [
            ObjectId(template_id) for template_id in client.get("templates", [])
        ]

        if not template_ids:
            self._templates = []
            return

        templates_query = {"_id": {"$in": template_ids}}

        if not client["is_dev"]:
            templates_query.update({"enabled": True, "dev": False})

        self._templates = [
            template["name"]
            for template in await mongo.find(
                "templates",
                templates_query,
                {"_id": 0, "name": 1},
            )
        ]

    
