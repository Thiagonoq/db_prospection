from enum import Enum
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic_core import core_schema


class GPTRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
