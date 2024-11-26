from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

import config
import logging

DEV = config.DEV
uri = config.MONGODB_URI #if not DEV else "mongodb://localhost:27017"
DB_NAME = config.MONGODB_NAME


class MongoDB:

    def __init__(self):
        self.client = AsyncIOMotorClient(uri, tz_aware=True)
        self.db = self.client[DB_NAME]
        logging.info("Conectado ao MongoDB.")

    def get_collection(self, collection_name: str):
        return self.db[collection_name]
    
    async def index_information(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection = self.get_collection(collection_name)
            return await collection.index_information()
        except Exception as e:
            logging.error(f"Erro ao obter informações de índice na coleção {collection_name}: {e}")
            return {}
    
    async def find(self, collection_name: str, query: Dict[str, Any], user_filter: Dict[str, Any] = {}) -> list[dict]:
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query, user_filter)
            return await cursor.to_list(length=None)
        except Exception as e:
            logging.error(f"Erro ao buscar no MongoDB: {e}")        
            return []
    
    async def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            collection = self.get_collection(collection_name)
            return await collection.find_one(query)
        except Exception as e:
            logging.error(f"Erro ao buscar um documento no MongoDB: {e}")
            return None
        
    async def get_config(self, data: dict = {}):
        try:
            collection = self.get_collection("config")
            return await collection.find_one({}, {"_id": 0}.update(data))
        except Exception as e:
            logging.error(f"Erro ao buscar um documento no MongoDB: {e}")
            return None
    
    async def find_one_and_update(
        self,
        collection_name: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        return_document: ReturnDocument = ReturnDocument.AFTER
    ) -> Optional[Dict[str, Any]]:
        try:
            collection = self.get_collection(collection_name)
            return await collection.find_one_and_update(filter, update, return_document=return_document)
        except Exception as e:
            logging.error(f"Erro ao buscar e atualizar um documento no MongoDB: {e}")
            return None
    
    async def count_documents(self, collection_name: str, query: Dict[str, Any]) -> int:
        try:
            collection = self.get_collection(collection_name)
            return await collection.count_documents(query)
        except Exception as e:
            logging.error(f"Erro ao contar documentos no MongoDB: {e}")
            return 0
        
    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Any:
        try:
            collection = self.get_collection(collection_name)
            return await collection.insert_one(document)
        except Exception as e:
            logging.error(f"Erro ao inserir um documento no MongoDB: {e}")
            return None

    async def update_one(
        self,
        collection_name: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False
    ) -> Any:
        try:
            collection = self.get_collection(collection_name)
            return await collection.update_one(query, update, upsert=upsert)
        except Exception as e:
            logging.error(f"Erro ao atualizar um documento no MongoDB: {e}")
            return None

    async def update_many(
        self,
        collection_name: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False
    ) -> Any:
        try:
            collection = self.get_collection(collection_name)
            return await collection.update_many(query, update, upsert=upsert)
        except Exception as e:
            logging.error(f"Erro ao atualizar vários documentos no MongoDB: {e}")
            return None
        
    async def delete_one(
        self,
        collection_name: str,
        query: Dict[str, Any]
    ) -> Any:
        try:
            collection = self.get_collection(collection_name)
            return await collection.delete_one(query)
        except Exception as e:
            logging.error(f"Erro ao deletar um documento no MongoDB: {e}")
            return None

mongo = MongoDB()