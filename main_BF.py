import asyncio
from datetime import datetime, timedelta, time
import logging
import os
import random
import re
import aiohttp
import uuid
from bson import ObjectId
from pymongo import ReturnDocument

import config
from src.database.mongo import mongo
from utils.zapi import Zapi
from utils.logging_config import setup_logging
from src.helpers.auth import create_login_url
from src.helpers.auth import create_template

now = datetime.now()

log_path = os.path.join(
    os.getcwd(),
    "log",
    str(now.year),
    f"{now.month:02d}",
    f"{now.day:02d}"
)

setup_logging(log_path)

def enable_to_prospect(now):
    """
    Verifica se o dia não é domingo e se o horário atual está dentro do horário de prospeção.
    """
    if now.weekday() == 6:
        return False

    start_hour = 8
    end_hour = 20
    return start_hour <= now.hour <= end_hour


async def wait_for_instance_status(session, zapi, zapi_instance, prospector_name, initial_delay=250, max_delay=3600, max_retries=None):
    """
    Aguarda pelo status da instância ZAPI.
    """
    delay = initial_delay
    retries = 0
    while not await zapi.get_instance_status(session):
        if max_retries is not None and retries >= max_retries:
            logging.error(f"Instância ZAPI {zapi_instance} de {prospector_name} não conectada. Abortando prospeção.")
            return False
        
        logging.error(f"Instância ZAPI {zapi_instance} de {prospector_name} não conectada, tentando novamente em {delay / 60:.2f} minutos")
        await asyncio.sleep(random.randint(delay * 0.8, delay * 1.2))    

        delay = min(delay * 2, max_delay)
        retries += 1

    return True

async def prospection(prospector_name, zapi_instance, zapi_token, zapi_client_token, instance_id, google = False):
    async with aiohttp.ClientSession() as session:
        zapi = Zapi(zapi_instance, zapi_token, zapi_client_token)

        while True:
            connected = await wait_for_instance_status(session, zapi, zapi_instance, prospector_name)

            if not connected:
                await asyncio.sleep(random.randint(50, 70))
                continue
            
            now = datetime.now()

            if enable_to_prospect(now):
                prospection_query = {
                    "prospection_date": {"$exists": False},
                    "prospector": prospector_name,
                    "assigned_to": {"$exists": False}
                }

                if google:
                    prospection_query["bd"] = "google"

                if config.DEV:
                    prospection_query = {
                        "phone": "553198929068",
                        "prospector": prospector_name
                    }

                try:
                    prospect = await mongo.find_one_and_update(
                        "prospecting_BF",
                        filter=prospection_query,
                        update={
                            "$set": {
                                "assigned_to": instance_id,
                                "assigned_at": datetime.now()
                            }
                        },
                        return_document=ReturnDocument.AFTER
                    )
                    if not prospect:
                        logging.info(f"Sem prospecções para {prospector_name}")
                        for support_number in config.SUPPORT_NUMBERS:
                            await zapi.send_message(session, support_number, f"Minha lista de prospecção está vazia!")

                        return
                    
                except Exception as e:
                    logging.exception(f"Erro ao buscar prospecções para {prospector_name}: {e}")
                    await asyncio.sleep(random.randint(50, 70))
                    continue

                try:
                    phone = re.sub(r"\D", "", str(prospect["phone"]))
                    whatsapp_number = await zapi.check_phone_exists(session, phone)

                    if not whatsapp_number:
                        logging.info(f"Telefone {phone} não possui WhatsApp")
                        query = {"_id": prospect["_id"]}
                        update = {
                            "$set": {
                                "no_whatsapp": True
                                },
                            "$unset": {
                                "assigned_to": "",
                                "assigned_at": ""
                            }
                        }
                        await mongo.update_one("prospecting_BF", query=query, update=update)
                        await asyncio.sleep(random.randint(3, 6))
                        continue
                    
                    await asyncio.sleep(random.randint(3, 6))
                    
                    prospect_client = await mongo.find_one("clients", {"client": phone})
                    prospect_client_id = prospect_client["_id"]
                    prospect_name = prospect_client.get("info", {}).get("name", "")
                    prospect_image = await create_template(prospect_client_id)

                    prospector_audio = config.BF_AUDIO[prospector_name]
                    audio_sended = await zapi.send_audio(session, whatsapp_number, prospector_audio)
                    
                    prospect_link = await create_login_url(prospect_client_id)
                    prospect_message = f"Olá{f', {prospect_name}' if prospect_name else ''}!\nSegue o link para as artes de divulgação dos seus produtos. 🎨\nDeixamos 10 modelos gratuitos disponíveis exclusivamente para você!\n\n👇 Só clicar no link abaixo e editar com seus produtos e preços: \n{prospect_link}\n\n🛒 Aproveite e destaque seus produtos com facilidade!"
                    await asyncio.sleep(random.randint(7, 13))
                    image_sended = await zapi.send_image(session, whatsapp_number, prospect_image, prospect_message)

                    if audio_sended and image_sended:
                        query = {"_id": prospect["_id"]}
                        update = {
                            "$set": {
                                "phone": whatsapp_number if isinstance(whatsapp_number, str) else phone,
                                "prospection_date": datetime.now()
                            },
                            "$unset": {
                                "assigned_to": "",
                                "assigned_at": ""
                            }
                        }
                        await mongo.update_one("prospecting_BF", query=query, update=update)
                        
                        logging.info(f"Prospecção de {prospector_name} aguardando 5 minutos...")
                        await asyncio.sleep(random.randint(280, 320))
                    
                    else:
                        logging.error(f"Erro ao enviar mensagem para {phone} com o prospector {prospector_name}")
                        query = {"_id": prospect["_id"]}
                        update = {
                            "$unset": {
                                "assigned_to": "",
                                "assigned_at": ""
                                }
                        }
                        await mongo.update_one("prospecting_BF", query=query, update=update)
                        logging.info(f"Prospecção de {prospector_name} aguardando 45 a 60 segundos...")
                        await asyncio.sleep(random.randint(45, 60))
                    
                except Exception as e:
                    prospect_name = prospect.get("name", "Nome desconhecido")
                    logging.exception(f"Erro ao prospectar {prospect_name} com o prospector {prospector_name}: {e}")
                    query = {"_id": prospect["_id"]}
                    update = {
                        "$unset": {
                            "assigned_to": "",
                            "assigned_at": ""
                            }
                    }
                    await mongo.update_one("prospecting_BF", query=query, update=update)
                    logging.info(f"Prospecção de {prospector_name} aguardando 45 a 60 segundos...")
                    await asyncio.sleep(random.randint(45, 60))

            else:
                logging.info(f"Prospecção fora do horário. Aguardando 10 minutos...")
                await asyncio.sleep(600)

async def clear_old_assigned_tasks():
    while True:
        try:
            query = {
                "assigned_to": {
                    "$exists": True
                },
                "assigned_at": {
                    "$lt": datetime.now() - timedelta(minutes=10)
                }
            }
            update = {
                "$unset": {
                    "assigned_to": "",
                    "assigned_at": ""
                }
            }

            if await mongo.count_documents("prospecting_BF", query) > 0:
                await mongo.update_many("prospecting_BF", query, update)

                logging.info("Limpeza de tarefas antiga concluída.")

        except Exception as e:
            logging.exception(f"Erro ao limpar tarefas antiga: {e}")
            await asyncio.sleep(100)
            continue

        await asyncio.sleep(600)
    
async def main():
    try:
        prospectors_data = await mongo.find("sellers", {})
    
    except Exception as e:
        logging.exception(f"Erro ao buscar configuração: {e}")
        return
    
    zapi_client_token = config.ZAPI_CLIENT_TOKEN

    tasks = []
    for prospector in prospectors_data:
        prospector_name = prospector["name"].replace(" - Video AI", "")
        if prospector_name not in config.ZAPI_CREDENTIALS:
            logging.warning(f"Configuração para {prospector_name} ausente. Tarefa de prospecção não iniciada.")
            continue

        try:
            zapi_credentials = config.ZAPI_CREDENTIALS.get(prospector_name, {})
            primary = zapi_credentials.get("primary", [None, None])
            secondary = zapi_credentials.get("secondary", [None, None])

            primary_instance, primary_token = primary
            secondary_instance, secondary_token = secondary


            if primary_instance and primary_token:
                primary_instance_id = str(uuid.uuid4())
                task_primary = asyncio.create_task(prospection(
                    prospector_name,
                    primary_instance,
                    primary_token,
                    zapi_client_token,
                    primary_instance_id,
                    google=False
                ))
                tasks.append(task_primary)
            else:
                logging.info(f"Instância primária para {prospector_name} está incompleta. Tarefa primária não iniciada.")

            if secondary_instance and secondary_token:
                secondary_instance_id = str(uuid.uuid4())
                task_secondary = asyncio.create_task(prospection(
                    prospector_name,
                    secondary_instance,
                    secondary_token,
                    zapi_client_token,
                    secondary_instance_id,
                    google=False
                ))
                tasks.append(task_secondary)
            else:
                logging.warning(f"Instância secundária para {prospector_name} está incompleta. Tarefa secundária não iniciada.")
        except Exception as e:
            logging.exception(f"Erro ao criar tarefa para {prospector_name}: {e}")
            continue
    
    if tasks:
        try:
            cleanup_task = asyncio.create_task(clear_old_assigned_tasks())
            tasks.append(cleanup_task)

            await asyncio.gather(*tasks)
        except Exception as e:
            logging.exception(f"Erro durante a execução das tarefas: {e}")
    
    else:
        logging.warning("Nenhuma tarefa de prospecção foi iniciada.")

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        logging.exception(f"Erro geral: {e}")