import os
import operator
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END

# --- 1. KURULUM ve AYARLAR ---
load_dotenv()
model_name = os.getenv("GEMINI_MODEL_NAME")
if not model_name:
    raise ValueError("GEMINI_MODEL_NAME ortam değişkeni bulunamadı.")

# Ajanın Kişiliği (System Prompt)
AGENT_PERSONA = """
Sen, sorulara her zaman net, kısa ve anlaşılır cevaplar veren bir uzmansın. 
Karmaşık konuları bile basit bir dille açıklarsın. 
Cevapların profesyonel ama samimi olmalı. 
Kullanıcının adını biliyorsan ona adıyla hitap et.
"""

# --- 2. DURUM (STATE) TANIMI ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 3. ARAÇ (TOOL) TANIMI ---
tools = [TavilySearch(max_results=2)]
tools_by_name = {tool.name: tool for tool in tools}

# --- 4. GRAF DÜĞÜMLERİ (NODES) ---
def call_model(state: AgentState):
    print("---DÜŞÜNÜLÜYOR---")
    llm = init_chat_model(model_name, model_provider="google_genai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def call_tool(state: AgentState):
    print("---ARAÇ KULLANILIYOR---")
    last_message = state["messages"][-1]
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        print(f"Araç çağrısı: {tool.name} with args {tool_call['args']}")
        observation = tool.invoke(tool_call["args"])
        tool_messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        
    return {"messages": tool_messages}

# --- 5. GRAFIN OLUŞTURULMASI ve KENARLARIN TANIMLANMASI ---
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "action"
    else:
        return "end"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"action": "action", "end": END})
workflow.add_edge("action", "agent")

app = workflow.compile()

# --- 6. ANA ÇALIŞTIRMA DÖNGÜSÜ ---
print(f"'{model_name}' modeli ile LangGraph ajanı hazır!")
print("Soru sorabilirsiniz. Çıkmak için 'q' veya 'quit' yazın.")

# Konuşma geçmişini tutacak olan listeyi döngünün DIŞINDA tanımlıyoruz.
conversation_history = [
    # Ajanın kişiliğini en başa bir sistem mesajı olarak ekliyoruz.
    AIMessage(content=AGENT_PERSONA)
]

while True:
    user_input = input("Siz: ")
    if user_input.lower() in ["q", "quit"]:
        print("Bot kapatılıyor.")
        break

    # Kullanıcının yeni mesajını geçmişe ekliyoruz.
    conversation_history.append(HumanMessage(content=user_input))

    # Grafı çalıştırırken artık TÜM konuşma geçmişini gönderiyoruz.
    inputs = {"messages": conversation_history}
    response = app.invoke(inputs)

    # Ajanın son cevabını da geçmişe ekliyoruz ki bir sonraki turda hatırlasın.
    final_response_message = response["messages"][-1]
    conversation_history.append(final_response_message)
    
    print(f"Bot: {final_response_message.content}")