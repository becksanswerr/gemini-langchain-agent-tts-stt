import os
import operator
import time
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END

# Yerel dosyalardan importlar
from config import AGENT_PERSONA
from tools.custom_tools import read_todo_list, send_message

# --- 1. KURULUM ve AYARLAR ---
load_dotenv()
model_name = os.getenv("GEMINI_MODEL_NAME")

# --- 2. DURUM (STATE) TANIMI ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 3. ARAÇLARIN BİRLEŞTİRİLMESİ ---
tools = [read_todo_list, send_message]
tools_by_name = {tool.name: tool for tool in tools}

# --- 4. GRAF DÜĞÜMLERİ (NODES) ---

def call_model(state: AgentState):
    print("---DÜŞÜNÜLÜYOR---")
    llm = init_chat_model(model_name, model_provider="google_genai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def human_approval_node(state: AgentState):
    print("---İNSAN ONAYI BEKLENİYOR---")
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    
    prompt = (
        f"Ajan şu eylemi gerçekleştirmek istiyor:\n"
        f"ARAÇ: {tool_call['name']}\n"
        f"PARAMETRELER: {tool_call['args']}\n"
        f"Onaylıyor musunuz? (evet/hayir): "
    )
    
    response = input(prompt).lower().strip()
    
    if response == "evet":
        return {"messages": [AIMessage(content="Kullanıcı eylemi onayladı.")]}
    else:
        return {"messages": [AIMessage(content="Kullanıcı eylemi reddetti. Durumu kullanıcıya bildir.")]}


def call_tool(state: AgentState):
    print("---ARAÇ KULLANILIYOR---")
    tool_call_message = next(msg for msg in reversed(state['messages']) if msg.tool_calls)
    
    tool_messages = []
    for tool_call in tool_call_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        print(f"Araç çağrısı: {tool.name} with args {tool_call['args']}")
        observation = tool.invoke(tool_call['args'])
        tool_messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        
    return {"messages": tool_messages}

# --- 5. GRAFIN OLUŞTURULMASI ve KENARLARIN TANIMLANMASI ---

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    
    if last_message.tool_calls[0]["name"] == "send_message":
        return "human_approval"
    else:
        return "action"
    
def after_approval(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if "Kullanıcı eylemi onayladı." in last_message.content:
        return "action"
    else:
        return "agent"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"human_approval": "human_approval", "action": "action", "end": END})
workflow.add_conditional_edges("human_approval", after_approval, {"action": "action", "end": "agent"})
workflow.add_edge("action", "agent")

app = workflow.compile()

# --- 6. SİMÜLASYON BAŞLANGICI ---
def simulate_live_notification(sender: str, message: str):
    print("\n" + "="*40)
    print("🔔 YENİ BİLDİRİM 🔔")
    print("="*40)
    time.sleep(1)
    print(f"Gönderen: {sender}")
    print(f"Mesaj: {message}")
    print("="*40 + "\n")
    time.sleep(1)

simulate_live_notification("Ecem", "bu gun napicaksin")

initial_prompt = """
GELEN OLAY: Ecem adlı kişiden yeni bir mesaj alındı.
MESAJ İÇERİĞİ: "bu gun napicaksin"
GÖREV: Bu duruma uygun şekilde tepki ver. Gerekli araçları kullanarak bir eylem planı oluştur ve uygula.
"""

conversation_history = [
    AIMessage(content=AGENT_PERSONA),
    HumanMessage(content=initial_prompt)
]

print("--- AJAN TETİKLENDİ ---")
inputs = {"messages": conversation_history}

for event in app.stream(inputs, stream_mode="values"):
    last_message = event["messages"][-1]
    
    if isinstance(last_message, AIMessage) and not last_message.tool_calls:
        print(f"Bot: {last_message.content}")

print("\n--- İŞ AKIŞI TAMAMLANDI ---")