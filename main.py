import asyncio
from datetime import datetime, timedelta
import json
import logging
import os
import random
import re

import aiohttp
import pytz

import config
from src.database.mongo import mongo
from utils.agendor import agendor

log_path = os.path.join(os.getcwd(), "log")
if not os.path.exists(log_path):
    os.mkdir(log_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_path, "card.log")),
        logging.StreamHandler()
    ]
)
tz = pytz.timezone("America/Sao_Paulo")

def get_greetings():
    now = datetime.now(tz=tz)
    hour = now.hour

    if 6 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    elif 18 <= hour < 24 or hour < 6:
        return "Boa noite"

def enable_to_prospect(now):
    start_hour = 8
    end_hour = 21
    return start_hour <= now.hour <= end_hour

async def sleep_until_tomorrow(prospector):
    now = datetime.now(tz=tz)
    tomorrow = now + timedelta(days=1).replace(hour=0, minute=0, second=0, microsecond=0)
    sleep_time = (tomorrow - now).total_seconds()

    logging.info(f"Limite de prospeções diárias atingido para {prospector}. Aguardando {format(sleep_time / 60, '.2f')} Minutos.")
    await asyncio.sleep(sleep_time)

async def send_message(mongo_id, session, message, phone, zapi_instance, zapi_token, zapi_client_token):
    url = f"https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/"
    formated_phone = re.sub(r"\D", "", str(phone))
    has_whatsapp = False

    try:
        async with session.get(f"{url}phone-exists/{formated_phone}") as response:
            if response.status == 200:
                has_whatsapp = True
            else:
                has_whatsapp = False

    except Exception as e:
        logging.exception(f"Erro ao verificar se o telefone {phone} tem WhatsApp: {e}")
        has_whatsapp = False

    if not has_whatsapp:
        logging.error(f"O telefone {phone} não tem WhatsApp")
        query = {"_id": mongo_id}
        update = {
            "$set": {
                "no_whatsapp": True
            }
        }
        mongo.update_one("SDR_prospecting", query=query, update=update)
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": zapi_client_token
    }

    payload = {
        "phone": phone,
        "message": message
    }

    try:
        async with session.post(f"{url}send-text", headers=headers, json=payload) as response:
            if response.status == 200:
                logging.info(f"Mensagem enviada para {phone}")
                return True
            else:
                logging.error(f"Erro ao enviar mensagem para o telefone {phone}: {response.status} {response.reason}")
                return False

    except Exception as e:
        logging.exception(f"Erro ao enviar mensagem para o telefone {phone}: {e}")
        return False

def choose_message(prospector):
    with open("greeting_messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
    
    message = random.choice(messages)
    return message.format(prospector=prospector)

async def prospection(prospector, zapi_instance, zapi_token, zapi_client_token):
    async with aiohttp.ClientSession() as session:
        while True:
            now = datetime.now(tz=tz)

            if enable_to_prospect():
                today_start = datetime(now.year, now.month, now.day, tzinfo=pytz.utc)
                num_prospections_query = {
                    "prospection_date": {"$gte": today_start},
                    "prospector": prospector
                }
                try:
                    num_prospections = await mongo.count_documents("SDR_prospecting", query=num_prospections_query)
                
                except Exception as e:
                    print(f"Erro ao contar prospeções: {e}")
                    await asyncio.sleep(60)
                    continue

                if num_prospections > 300:
                    await sleep_until_tomorrow(prospector)
                    continue

                prospection_query = {
                    "prospection_date": {"$exists": False},
                    "prospector": prospector,
                    "no_whatsapp": {
                        "$exists": False,
                        "$nin": [True]
                    }
                }
                try:
                    prospection_data = await mongo.find("SDR_prospecting", query=prospection_query)

                except Exception as e:
                    logging.exception(f"Erro ao buscar prospeções para {prospector}: {e}")
                    await asyncio.sleep(60)
                    continue

                for prospect in prospection_data:
                    prospect_name = prospect["name"]
                    try:
                        message = choose_message(prospector)

                        message_sent = send_message(prospect["_id"], session, message, prospect["phone"], zapi_instance, zapi_token, zapi_client_token)

                        if message_sent:
                            agendor.update_deal_stage(prospect["agendor_deal_id"], 3)

                            query = {"_id": prospect["_id"]}
                            update = {"$set": {"prospection_date": now}}
                            await mongo.update_one("SDR_prospecting", query=query, update=update)
                        
                    except Exception as e:
                        logging.exception(f"Erro ao prospeccar {prospect_name}o prospector {prospector}: {e}")
                    
                    finally:
                        logging.info(f"Prospeccão de {prospector} aguardando 3 minutos...")
                        await asyncio.sleep(180)

            else:
                logging.info(f"Prospecção fora do horário. Aguardando 10 minutos...")
                await asyncio.sleep(600)

async def main():
    try:
        config_data = await mongo.find_one("config", {})
        prospectors_data = config_data.get("agendor_allowed_users", [])
    
    except Exception as e:
        print(f"Erro ao buscar configuração: {e}")
        return
    
    prospectors = {prospector["name"]: prospector["phone"] for prospector in prospectors_data}
    zapi_client_token = config.ZAPI_CLIENT_TOKEN

    tasks = []
    for prospector in prospectors:
        try:
            zapi_instance = config.ZAPI_INSTANCE[prospector]
            zapi_token = config.ZAPI_TOKEN[prospector]
            task = asyncio.create_task(prospection(prospector, zapi_instance, zapi_token, zapi_client_token))
            tasks.append(task)
        
        except Exception as e:
            logging.exception(f"Erro ao criar tarefa para {prospector}: {e}")
            continue
    
    if tasks:
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.exception(f"Erro durante a execução das tarefas: {e}")
    
    else:
        logging.warning("Nenhuma tarefa de prospecção foi iniciada.")

if __name__ == "__main__":
    asyncio.run(main())