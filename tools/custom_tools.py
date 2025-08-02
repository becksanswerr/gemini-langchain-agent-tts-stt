from langchain_core.tools import tool


FAKE_TODO_LIST = "Bugün için planlanmış bir şey yok."

@tool
def read_todo_list():
    """Bugünün yapılacaklar listesini kontrol etmek için kullanılır. Girdi almaz."""
    print("--- ARAÇ: To-do listesi okunuyor... ---")
    return FAKE_TODO_LIST

@tool
def send_message(recipient: str, message: str):
    """Belirtilen kişiye bir mesaj gönderir. Kime ve ne gönderileceğini belirtir."""
    print(f"--- ARAÇ: '{recipient}' kişisine mesaj gönderiliyor: '{message}' ---")
    return "Mesaj başarıyla gönderildi."