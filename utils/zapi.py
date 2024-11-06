import aiohttp
import logging

class Zapi:
    def __init__(self, instance_id:str, token: str, client_token: str) -> None:
        self.instance = instance_id
        self.token = token
        self.client_token = client_token
        self.url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
        self.headers = {
            "Content-Type": "application/json",
            "Client-Token": client_token
        }

    async def get_instance_status(self, session: aiohttp.ClientSession) -> bool:
        url = f"{self.url}/status"
        try:
            async with session.get(url, headers=self.headers) as response:
                data = await response.json()
                if response.status == 200 and data["connected"]:
                    logging.info(f"Instância ZAPI conectada: {self.instance}")
                    return True
                
                else:
                    error_msg = data.get("error", "Erro desconhecido")
                    logging.error(f"instância ZAPI não conectada: {self.instance}: {error_msg}")
                    return False

        except Exception as e:
            logging.exception(f"Erro ao checar a instância ZAPI {self.instance}: {e}")
            return False

    async def check_phone_exists(self, session: aiohttp.ClientSession, phone: str) -> bool:
        url = f"{self.url}/phone-exists/{phone}"
        try:
            async with session.get(url, headers=self.headers) as response:
                data = await response.json()
                if response.status == 200 and data.get("exists", False):
                    logging.info(f"Telefone {phone} existe no Whatsapp: {self.instance}")
                    return data.get("phone", True)
                
                else:
                    logging.error(f"Telefone {phone} não existe no Whatsapp: {self.instance}")
                    return False

        except Exception as e:
            logging.exception(f"Erro ao checar o telefone {phone} no ZAPI {self.instance}: {e}")
            return False
    
    async def send_message(self, session: aiohttp.ClientSession, phone: str, message: str) -> bool:
        url = f"{self.url}/send-text"
        payload = {
            "phone": phone,
            "message": message
        }
        try:
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    logging.info(f"Message sent to {phone}")
                    return True
                
                else:
                    logging.error(f"Failed to send message to {phone}: {response.status} {response.reason}")
                    return False
                
        except Exception as e:
            logging.exception(f"Error sending message to {phone}: {e}")
            return False
    
    async def send_button_text(self, session: aiohttp.ClientSession, phone: str, message: str, buttons: list) -> bool:
        url = f"{self.url}/send-button-list"
        buttons_data = []
        for i, button in enumerate(buttons):
            buttons_data.append({
                "id": i,
                "label": button
            })

        payload = {
            "phone": phone,
            "message": message,
            "buttonList": {
                "buttons": buttons_data

            }
        }

        try:
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    logging.info(f"Message sent to {phone}")
                    return True
                
                else:
                    logging.error(f"Failed to send message to {phone}: {response.status} {response.reason}")
                    return False
                
        except Exception as e:
            logging.exception(f"Error sending message to {phone}: {e}")
            return False