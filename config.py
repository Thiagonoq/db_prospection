import dotenv
import os

dotenv.load_dotenv()

DEV = os.getenv("DEV") == "true"

SUPPORT_NUMBERS = ["553198929068"]
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = 'videoai'

AGENDOR_TOKEN = os.getenv("AGENDOR_TOKEN")

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")

ZAPI_CREDENTIALS = {
    "Stênio": {
        "primary": (os.getenv("ZAPI_STENIO1_TOKEN"), os.getenv("ZAPI_STENIO1_INSTANCE")),
        "secondary": (os.getenv("ZAPI_STENIO2_TOKEN"), os.getenv("ZAPI_STENIO2_INSTANCE"))
    },
    "Michelly": {
        "primary": (os.getenv("ZAPI_MICHELLY1_TOKEN"), os.getenv("ZAPI_MICHELLY1_INSTANCE")),
        "secondary": (os.getenv("ZAPI_MICHELLY2_TOKEN"), os.getenv("ZAPI_MICHELLY2_INSTANCE"))
    },
    "Ana Paula": {
        "primary": (os.getenv("ZAPI_ANA_PAULA1_TOKEN"), os.getenv("ZAPI_ANA_PAULA1_INSTANCE")),
        "secondary": (os.getenv("ZAPI_ANA_PAULA2_TOKEN"), os.getenv("ZAPI_ANA_PAULA2_INSTANCE"))
    }
}

ZAPI_ENDPOINT = os.getenv("ZAPI_ENDPOINT")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

# ZAPI_TOKEN = {
#     "Stênio": os.getenv("ZAPI_STENIO_TOKEN"),
#     "Michelly": os.getenv("ZAPI_MICHELLY_TOKEN"),
#     "Ana Paula": os.getenv("ZAPI_ANA_PAULA_TOKEN")
# }
# ZAPI_INSTANCE = {
#     "Stênio": os.getenv("ZAPI_STENIO_INSTANCE"),
#     "Michelly": os.getenv("ZAPI_MICHELLY_INSTANCE"),
#     "Ana Paula": os.getenv("ZAPI_ANA_PAULA_INSTANCE")
# }