from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.helpers import date


class BaseUsage(BaseModel):
    failed: int = 0
    success: int = 0
    cancelled: int = 0


class SendedMessages(BaseModel):
    text: int = 0
    audio: int = 0
    image: int = 0


class GPTAvailableModels(str, Enum):
    gpt_4o = "gpt-4o"
    gpt_3_5_turbo_0125 = "gpt-3.5-turbo-0125"
    gpt_3_5_turbo_1106 = "gpt-3.5-turbo-1106"
    gpt_4_1106_preview = "gpt-4-1106-preview"
    gpt_4_vision_preview = "gpt-4-vision-preview"
    whisper = "whisper-1"


class GPTModel(BaseModel):
    name: GPTAvailableModels


class GPTTextModel(GPTModel):
    completionTokens: int = 0
    promptTokens: int = 0
    expense: float = 0


class GPTWhisperModel(GPTModel):
    seconds: float = 0
    expense: float = 0


GPTModels = GPTTextModel | GPTWhisperModel


class Usage(BaseModel):
    created: BaseUsage
    edited: BaseUsage


class GPT(BaseModel):
    usage: list[GPTModels] = []


class FlowAnalytics(BaseModel):
    started: datetime
    ended: Optional[datetime] = None


class TemplateAnalytics(BaseModel):
    name: str
    published: int = 0
    requestedCatalog: int = 0

    sended: SendedMessages = SendedMessages()
    usage: Usage = Usage(created=BaseUsage(), edited=BaseUsage())

    gpt: GPT = GPT()

    flows: list[FlowAnalytics] = []


class Sources(str, Enum):
    sms = "sms"
    site = "site"
    email = "email"
    other = "other"
    tiktok = "tiktok"
    youtube = "youtube"
    facebook = "facebook"
    whatsapp = "whatsapp"
    instagram = "instagram"
    google_search = "google_search"
    indication = "indication"
    agent = "agent"
    agent_marcelo = "agent_marcelo"
    agent_ana_carolina = "agent_ana_carolina"


class Segments(str, Enum):
    dentist = "dentist"
    optics = "optics"
    construction_material = "construction_material"
    vehicle_store = "vehicle_store"
    burger = "burger"
    pizzaria = "pizzaria"
    restaurant = "restaurant"
    clothing_and_apparel = "clothing_and_apparel"
    hardware_and_technology = "hardware_and_technology"
    smartphone_and_accessories = "smartphone_and_accessories"
    real_estate = "real_estate"
    shoes = "shoes"
    butchers = "butchers"
    supermarket = "supermarket"
    pet_shop = "pet_shop"
    stationery_shop = "stationery_shop"
    academy = "academy"
    pharmacy = "pharmacy"
    watches_and_jewelry = "watches_and_jewelry"
    bakery = "bakery"
    hortifruti = "hortifruti"
    political = "political"
    others = "others"


class AnalyticsModel(BaseModel):
    client: str

    templates: list[TemplateAnalytics] = []

    created_at: datetime = date.now()
    updated_at: datetime = date.now()
