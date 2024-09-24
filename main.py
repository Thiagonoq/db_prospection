import asyncio
from datetime import datetime, timedelta, time
import json
import logging
import os
import random
import re

import aiohttp

import config
from src.database.mongo import mongo
from utils.agendor import agendor
from utils.zapi import Zapi
from utils.logging_config import setup_logging

now = datetime.now()

log_path = os.path.join(
    os.getcwd(),
    "log",
    str(now.year),
    f"{now.month:02d}",
    f"{now.day:02d}"
)

setup_logging(log_path)

def get_greetings():
    now = datetime.now()
    hour = now.hour

    if 6 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def enable_to_prospect(now):
    """
    Verifica se o dia não é domingo e se o horário atual está dentro do horário de prospeção.
    """
    if now.weekday() == 6:
        return False

    start_hour = 8
    end_hour = 20
    return start_hour <= now.hour <= end_hour

async def sleep_until_tomorrow(prospector_name):
    """
    Aguarda pelo horário de prospeção do dia seguinte.
    """
    now = datetime.now()
    tomorrow_date = now.date() + timedelta(days=1)
    tomorrow = datetime.combine(tomorrow_date, time.min)

    sleep_time = (tomorrow - now).total_seconds()

    logging.info(f"Limite de prospecções diárias atingido para {prospector_name}. Aguardando {sleep_time / 3600:.2f} horas.")
    await asyncio.sleep(sleep_time)

def choose_message(prospector_name):
    with open("greeting_messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
    
    message = random.choice(messages)
    return message.format(prospector=prospector_name)


async def prospection(prospector_name, zapi_instance, zapi_token, zapi_client_token):
    async with aiohttp.ClientSession() as session:
        zapi = Zapi(zapi_instance, zapi_token, zapi_client_token)
        if not await zapi.get_instance_status(session):
            logging.error(f"Instância ZAPI {zapi_instance} de {prospector_name} não conectada")
            return
        
        while True:
            now = datetime.now()

            if enable_to_prospect(now):
                today_start = datetime(now.year, now.month, now.day)

                num_prospections_query = {
                    "prospection_date": {"$gte": today_start},
                    "prospector": prospector_name
                }
                try:
                    num_prospections = await mongo.count_documents("SDR_prospecting", query=num_prospections_query)
                
                except Exception as e:
                    logging.exception(f"Erro ao contar prospecções para {prospector_name}: {e}")
                    await asyncio.sleep(random.randint(50, 70))
                    continue

                if num_prospections > 300:
                    await sleep_until_tomorrow(prospector_name)
                    continue

                prospection_query = {
                    "prospection_date": {"$exists": False},
                    "prospector": prospector_name,
                    "no_whatsapp": {"$ne": True}
                }
                try:
                    prospection_data = await mongo.find("SDR_prospecting", query=prospection_query)

                except Exception as e:
                    logging.exception(f"Erro ao buscar prospecções para {prospector_name}: {e}")
                    await asyncio.sleep(random.randint(50, 70))
                    continue

                if not prospection_data:
                    logging.info(f"Sem prospecções para {prospector_name}")
                    await zapi.send_message(session, "553198929068", f"Minha lista de prospecção está vazia!")
                    return

                for prospect in prospection_data:
                    try:
                        message = choose_message(prospector_name)
                        phone = re.sub(r"\D", "", str(prospect["phone"]))

                        if not await zapi.check_phone_exists(session, phone):
                            logging.info(f"Telefone {phone} não possui WhatsApp")
                            query = {"_id": prospect["_id"]}
                            update = {"$set": {"no_whatsapp": True}}
                            await mongo.update_one("SDR_prospecting", query=query, update=update)
                            continue

                        if await zapi.send_message(session, phone, message):
                            agendor_deal_id = prospect.get("agendor_deal_id")
                            if agendor_deal_id:
                                agendor.update_deal_stage(prospect["agendor_deal_id"], 3)
                            else:
                                logging.info(f"Agendamento de Prospeção não encontrado para {prospector_name}")

                            query = {"_id": prospect["_id"]}
                            update = {"$set": {"prospection_date": datetime.now()}}
                            await mongo.update_one("SDR_prospecting", query=query, update=update)
                        
                    except Exception as e:
                        prospect_name = prospect.get("name", "Nome desconhecido")
                        logging.exception(f"Erro ao prospectar {prospect_name} com o prospector {prospector_name}: {e}")
                    
                    finally:
                        logging.info(f"Prospecção de {prospector_name} aguardando 3 minutos...")
                        await asyncio.sleep(random.randint(165, 195))

            else:
                logging.info(f"Prospecção fora do horário. Aguardando 10 minutos...")
                await asyncio.sleep(random.randint(165, 195))

async def main():
    try:
        config_data = await mongo.find_one("config", {})
        prospectors_data = config_data.get("agendor_allowed_users", [])
    
    except Exception as e:
        logging.exception(f"Erro ao buscar configuração: {e}")
        return
    
    zapi_client_token = config.ZAPI_CLIENT_TOKEN

    tasks = []
    for prospector in prospectors_data:
        prospector_name = prospector["name"]
        if prospector_name not in config.ZAPI_INSTANCE or prospector_name not in config.ZAPI_TOKEN:
            logging.warning(f"Configuração para {prospector_name} ausente. Tarefa de prospecção não iniciada.")
            continue

        try:
            zapi_instance = config.ZAPI_INSTANCE.get(prospector_name)
            zapi_token = config.ZAPI_TOKEN.get(prospector_name)
            task = asyncio.create_task(prospection(prospector_name, zapi_instance, zapi_token, zapi_client_token))
            tasks.append(task)
        
        except Exception as e:
            logging.exception(f"Erro ao criar tarefa para {prospector_name}: {e}")
            continue
    
    if tasks:
        try:
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