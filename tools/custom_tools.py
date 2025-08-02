# tools/custom_tools.py

import os
from langchain_core.tools import tool

FAKE_TODO_LIST = "Bugün için planlanmış bir şey yok."
# YENİ: Cevapların kaydedileceği klasörü ayrı bir değişken olarak tanımlıyoruz.
REPLIES_DIR = "sent_replies"

@tool
def read_todo_list():
    """Bugünün yapılacaklar listesini kontrol etmek için kullanılır. Girdi almaz."""
    print("--- ARAÇ: To-do listesi okunuyor... ---")
    return FAKE_TODO_LIST

@tool
def send_message(recipient: str, message: str):
    """Belirtilen kişiye bir mesaj gönderir. Kime ve ne gönderileceğini belirtir."""
    print(f"--- ARAÇ: '{recipient}' kişisine mesaj gönderiliyor: '{message}' ---")
    
    # GÜNCELLEME: Gönderilen cevabı 'sent_replies' klasörüne kaydet
    try:
        # Klasörün var olduğundan emin ol, yoksa oluştur.
        os.makedirs(REPLIES_DIR, exist_ok=True)
        
        reply_filename = f"reply_to_{recipient}.txt"
        # GÜNCELLEME: Dosya yolunu yeni klasörü kullanacak şekilde oluştur.
        reply_filepath = os.path.join(REPLIES_DIR, reply_filename)
        
        with open(reply_filepath, 'w', encoding='utf-8') as f:
            f.write(message)
        print(f"--- BİLGİ: Cevap '{reply_filepath}' dosyasına kaydedildi. ---")
    except Exception as e:
        print(f"--- HATA: Cevap dosyası kaydedilemedi: {e} ---")

    return "Mesaj başarıyla gönderildi."