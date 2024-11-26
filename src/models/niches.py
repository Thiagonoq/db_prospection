from pydantic import BaseModel

from src.models.analytics import Segments


class Dentist(BaseModel):
    specialty: str
    cro: str


def segmented_models(niche: Segments):
    return {Segments.dentist: Dentist}.get(niche)
