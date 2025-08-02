# listener.py

import os
import time
from agent_logic import run_agent_workflow

NOTIFICATIONS_DIR = "notifications"

def watch_for_notifications():
    os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)
    print("[Dinleyici]: Arka planda bildirimler dinleniyor...")
    
    while True:
        try:
            for filename in os.listdir(NOTIFICATIONS_DIR):
                if filename.endswith(".txt"):
                    filepath = os.path.join(NOTIFICATIONS_DIR, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        message_content = f.read().strip()
                    
                    sender = filename.split('_')[0]
                    
                    print(f"\n🔔 [Dinleyici]: Yeni bildirim algılandı: {sender} -> {message_content}")
                    
                    initial_prompt = (
                        f"GELEN OLAY: {sender} adlı kişiden yeni bir mesaj alındı.\n"
                        f"MESAJ İÇERİĞİ: \"{message_content}\"\n"
                        f"GÖREV: Bu duruma uygun şekilde tepki ver."
                    )
                    
                    # Dinleyici otonom çalıştığı için bayrak 'False' olacak.
                    run_agent_workflow(initial_prompt, invoked_by_user=False)
                    
                    os.remove(filepath)
            
            time.sleep(5)
        except Exception as e:
            print(f"[Dinleyici Hata]: {e}")
            time.sleep(10)