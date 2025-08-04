# database.py

import os
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB'ye bir kere bağlanıp istemciyi yeniden kullan
client = MongoClient(os.getenv("MONGO_URI"))
db = client.get_database("ai_agent_db") # Veritabanı adı
conversations_collection = db.get_collection("conversations") # Koleksiyon adı

def save_conversation(session_id: str, messages: list):
    """Konuşma geçmişini MongoDB'ye kaydeder veya günceller."""
    # Mesajları veritabanına uygun formata çevir
    #     db_messages = [msg.dict() for msg in messages]
    
    conversations_collection.update_one(
        {"_id": session_id},
        {"$set": {"messages": db_messages}},
        upsert=True # Eğer session_id yoksa yeni bir döküman oluştur
    )

def get_conversations():
    """Tüm geçmiş konuşmaları veritabanından çeker."""
    return list(conversations_collection.find())