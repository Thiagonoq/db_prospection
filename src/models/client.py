from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel

import config
from src.helpers import date
from src.models.analytics import Segments, Sources
from src.models.orders import OrderStatus


class ClientActions(str, Enum):
    edit_art = "edit_art"
    edit_art_template = "edit_art_template"
    publish_art = "publish_art"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Marketing(BaseModel):
    hashtags: Optional[list[str]] = []


class ClientInfoModel(BaseModel):
    name: Optional[str] = None

    cellphone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None

    marketing: Marketing = Marketing()

    extra: Optional[dict] = {}


class Purchase(BaseModel):
    type: OrderStatus = OrderStatus.free

    product_id: Optional[str] = None
    product_hash: Optional[str] = None

    use_limit: int = config.MAX_FREE_USE
    end_date: Optional[datetime] = None

    start_trial: datetime = date.now()
    free_trial_ended_date: Optional[datetime] = None


class Cta(BaseModel):
    recovery_user_register_first_message: bool = False
    recovery_user_register_trys: int = 0
    recovery_user_register_response: bool = False
    received_arts: int = 0


class ClientAnalytics(BaseModel):
    id: Optional[str] = None
    source: Sources = Sources.other


class ClientPreferences(BaseModel):
    newsletter: bool = True


class Narration(BaseModel):
    company_genre: str = "f"
    company_name: str = ""
    company_slogan: str = ""
    number_narration: str = ""


class Prospector(BaseModel):
    name: str = ""
    cellphone: str = ""


class CRM(BaseModel):
    id: Optional[int] = None
    deal_id: Optional[int] = None
    funnel_id: Optional[int] = None
    funnel_stage: Optional[int] = None


class Color(BaseModel):
    light: Optional[str] = None
    dark: Optional[str] = None


class Colors(BaseModel):
    primary: Optional[Color] = None
    secondary: Optional[Color] = None
    tertiary: Optional[Color] = None


class ClientModel(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    main_client: Optional[str] = None
    client: Optional[Union[list[str], str]] = []

    niche: Segments = "hortifruti"
    database: Segments = "hortifruti"

    purchase: Purchase = Purchase()
    analytics: ClientAnalytics = ClientAnalytics()
    preferences: ClientPreferences = ClientPreferences()
    cta: Cta = Cta()

    info: Optional[ClientInfoModel] = None

    options: dict = {
        "logo-border-is-dark": False,
        "style": {
            "bg-layer": {"effects": {"colorize": {"color": "#c9eeb1"}}},
            "color-primary": "#006805",
            "color-secondary": "#e1ffcd",
            "color-bg-primary": "#c9eeb1",
            "color-bg-secondary": "#006805",
            "color-bg-tertiary": "#3aa700",
        },
    }

    templates: list[str] = []
    narration: Narration = Narration()

    images: list[str] = ["logo.png", "dark-logo.png"]

    is_dev: bool = False
    has_logo: bool = False
    has_profile_logo: bool = False
    logo_by_designer: bool = False

    prospector: Prospector = Prospector()

    last_activity: Optional[datetime] = None
    created_at: datetime = date.now()

    crm: CRM = CRM()

    registered: bool = False
    is_tutorial: bool = True
    flow_state: Optional[str] = None
    synced: bool = False

    colors: Optional[Colors] = None
