# agent_logic.py

from langchain_core.messages import AIMessage, HumanMessage
from agent_core import app, AGENT_PERSONA

def run_agent_workflow(initial_prompt: str, invoked_by_user: bool):
    print("\n--- AJAN TETİKLENDİ ---")
    
    conversation_history = [
        AIMessage(content=AGENT_PERSONA),
        HumanMessage(content=initial_prompt)
    ]

    # GÜNCELLEME: Bayrağı grafa iletiyoruz.
    inputs = {
        "messages": conversation_history,
        "invoked_by_user": invoked_by_user
    }

    # Stream yerine invoke kullanalım, bu daha basit ve daha az hataya açık olacak.
    # Sadece nihai sonucu alacağız.
    final_state = app.invoke(inputs)
    last_message = final_state["messages"][-1]

    # Sadece nihai cevabı yazdır
    if isinstance(last_message, AIMessage) and not last_message.tool_calls:
        print(f"Bot: {last_message.content}")

    print("\n--- İŞ AKIŞI TAMAMLANDI ---")