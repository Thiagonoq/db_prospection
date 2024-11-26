import mimetypes
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, storage
import logging
import uuid

import config

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate({
                "type": "service_account",
                "private_key_id": config.FIREBASE_PRIVATE_KEY_ID,
                "private_key": config.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": config.FIREBASE_CLIENT_EMAIL,
                "client_id": config.FIREBASE_CLIENT_ID,
                "auth_uri": config.FIREBASE_AUTH_URI,
                "token_uri": config.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": config.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": config.FIREBASE_CLIENT_X509_CERT_URL
            })
            firebase_admin.initialize_app(cred, {'storageBucket': config.FIREBASE_STORAGE_BUCKET})
            logging.info("Aplicação Firebase inicializada com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao inicializar o Firebase: {e}")
            raise

def send_to_firebase(file_path: Path, main_client: str):
    file_name = file_path.name
    try:
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            logging.warning(f"Tipo MIME desconhecido para o arquivo {file_name}. Usando mime_type padrao.")
            return None
        
        if not (mime_type.startswith("video/") or mime_type.startswith("audio/") or mime_type.startswith("image/")):
            logging.info(f"Arquivo {file_name} com mime type {mime_type} não é de interesse. Pulando.")
            return None


        bucket = storage.bucket()

        blob = bucket.blob(f"prospection_BF/{main_client} - {str(uuid.uuid4())}/{file_name}")

        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, content_type=mime_type)
        logging.info(f"Arquivo {file_name} enviado para o Firebase Storage.")

        blob.make_public()
        url = blob.public_url
        logging.info(f"URL pública gerada para {file_name}: {url}")

        
        return url

    except Exception as e:
        logging.error(f"Erro ao enviar o arquivo {file_name} para o Firebase: {e}")
        return None
