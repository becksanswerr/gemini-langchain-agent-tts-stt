# database.py

import os
import json
from langchain_core.messages import message_to_dict

DB_DIR = "db"

def _get_filepath(session_id: str, prefix: str) -> str:
    """Belirli bir session için dosya yolunu oluşturur."""
    os.makedirs(DB_DIR, exist_ok=True)
    return os.path.join(DB_DIR, f"{prefix}_{session_id}.json")

def save_json_data(session_id: str, data: dict, prefix: str):
    """Veriyi belirtilen session için bir JSON dosyasına kaydeder."""
    filepath = _get_filepath(session_id, prefix)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json_data(session_id: str, prefix: str) -> dict | None:
    """Belirtilen session için JSON dosyasından veri yükler."""
    filepath = _get_filepath(session_id, prefix)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def delete_json_data(session_id: str, prefix: str):
    """Belirtilen session için JSON dosyasını siler."""
    filepath = _get_filepath(session_id, prefix)
    if os.path.exists(filepath):
        os.remove(filepath)

def save_conversation(session_id: str, messages: list):
    """Konuşma geçmişini bir JSON dosyasına kaydeder."""
    dict_messages = [message_to_dict(msg) for msg in messages]
    save_json_data(session_id, {"messages": dict_messages}, prefix="conv")

