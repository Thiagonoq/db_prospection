import dotenv
import os

dotenv.load_dotenv(override=True)

DEV = os.getenv("DEV") == "true"

SUPPORT_NUMBERS = ["553198929068"]
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = 'videoai'

AGENDOR_TOKEN = os.getenv("AGENDOR_TOKEN")

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")

VIDEOAI_API_TOKEN = os.getenv("VIDEOAI_API_TOKEN")

ZAPI_CREDENTIALS = {
    "Stênio": {
        "primary": (os.getenv("ZAPI_STENIO1_INSTANCE"), os.getenv("ZAPI_STENIO1_TOKEN")),
        "secondary": (os.getenv("ZAPI_STENIO2_INSTANCE"), os.getenv("ZAPI_STENIO2_TOKEN"))
    },
    "Michelly": {
        "primary": (os.getenv("ZAPI_MICHELLY1_INSTANCE"), os.getenv("ZAPI_MICHELLY1_TOKEN")),
        "secondary": (os.getenv("ZAPI_MICHELLY2_INSTANCE"), os.getenv("ZAPI_MICHELLY2_TOKEN"))
    },
    "Ana Paula": {
        "primary": (os.getenv("ZAPI_ANA_PAULA1_INSTANCE"), os.getenv("ZAPI_ANA_PAULA1_TOKEN")),
        "secondary": (os.getenv("ZAPI_ANA_PAULA2_INSTANCE"), os.getenv("ZAPI_ANA_PAULA2_TOKEN"))
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

BF_AUDIO = {
    "Ana Paula": "https://storage.googleapis.com/video-ai-bae31.appspot.com/prospection_BF/bf_ana.ogg",
    "Michelly": "https://storage.googleapis.com/video-ai-bae31.appspot.com/prospection_BF/bf_michelly.ogg",
    "Stênio": "https://storage.googleapis.com/video-ai-bae31.appspot.com/prospection_BF/bf_stenio.ogg"
}
BF_TEMPLATE = "6605bd3534db70ef71a34408"