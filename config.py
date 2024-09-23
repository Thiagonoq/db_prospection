import dotenv
import os

dotenv.load_dotenv()

DEV = os.getenv("DEV") == "true"

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = 'videoai'

AGENDOR_TOKEN = os.getenv("AGENDOR_TOKEN")

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")

ZAPI_TOKEN = {
    "Stênio": os.getenv("ZAPI_STENIO_TOKEN"),
    "Michelly": os.getenv("ZAPI_MICHELLY_TOKEN"),
    "Ana Paula": os.getenv("ZAPI_ANA_PAULA_TOKEN")
}
ZAPI_INSTANCE = {
    "Stênio": os.getenv("ZAPI_STENIO_INSTANCE"),
    "Michelly": os.getenv("ZAPI_MICHELLY_INSTANCE"),
    "Ana Paula": os.getenv("ZAPI_ANA_PAULA_INSTANCE")
}
ZAPI_ENDPOINT = os.getenv("ZAPI_ENDPOINT")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")