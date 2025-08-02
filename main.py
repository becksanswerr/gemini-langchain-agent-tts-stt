# main.py

import threading
from listener import watch_for_notifications
from agent_logic import run_agent_workflow

if __name__ == "__main__":
    listener_thread = threading.Thread(target=watch_for_notifications, daemon=True)
    listener_thread.start()

    print("Bot ile sohbet edebilirsiniz. Çıkmak için 'q' yazın.")
    
    while True:
        try:
            user_input = input("Siz: ")
            
            if user_input.lower() in ["q", "quit"]:
                break
            
            # Ana döngü her zaman kullanıcı tarafından başlatılır, bayrak 'True'.
            run_agent_workflow(user_input, invoked_by_user=True)

        except (KeyboardInterrupt, EOFError):
            break
    
    print("\nBot kapatılıyor.")