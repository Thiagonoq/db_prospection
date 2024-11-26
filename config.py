import logging
from pathlib import Path
import dotenv
import os
from openai import AsyncOpenAI

from src.handlers.log import DailyRotatingFileHandler

dotenv.load_dotenv(override=True)

DEV = os.getenv("DEV") == "true"

ABS_PATH = Path(__file__).parent.absolute()
TMP_PATH = ABS_PATH / ".tmp"
LOGS_PATH = ABS_PATH / "logs"

CARDS_PATH = ABS_PATH / "cards"
CLIENTS_PATH = ABS_PATH / "data/clients"
TEMPLATES_PATH = ABS_PATH / "data/templates"
SCRIPTS_PATH = ABS_PATH / "data/scripts"
IMAGES_PATH = ABS_PATH / "data/images"
DESIGNS_PATH = ABS_PATH / "data/designs"
TMP_PATH = ABS_PATH / ".tmp"
SERVER_URL = os.getenv("SERVER_URL")
CARD_SERVER_URL = SERVER_URL + "cards/"
REPOSITORY_IMAGES_URL = SERVER_URL + "repository/images/"
IMAGES_DATABASE_SERVER_URL = SERVER_URL + "database/"
GENERATED_CARD_IMAGES_PATH = Path(os.getenv("GENERATED_CARD_IMAGES_PATH"))
MAX_FREE_USE = 60

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_URL = os.getenv("ELEVENLABS_API_URL")

SUPPORT_NUMBERS = ["553198929068"]
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = 'videoai'

AGENDOR_TOKEN = os.getenv("AGENDOR_TOKEN")

OPENAI_APIKEY = os.getenv("OPENAI_APIKEY")

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


FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI")
FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI")
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
FIREBASE_CLIENT_X509_CERT_URL = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = DailyRotatingFileHandler(
    LOGS_PATH, maxBytes=10 * 1024 * 1024, backupCount=5
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# openai = AsyncOpenAI(api_key=OPENAI_APIKEY)

