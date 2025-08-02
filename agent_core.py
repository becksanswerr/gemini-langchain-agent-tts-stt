# agent_core.py

import os
import operator
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END

from config import AGENT_PERSONA
from tools.custom_tools import read_todo_list, send_message

load_dotenv()
model_name = os.getenv("GEMINI_MODEL_NAME")

# GÜNCELLEME: State'e kimin başlattığını belirten bayrağı geri ekliyoruz.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    invoked_by_user: bool

tools = [read_todo_list, send_message]
tools_by_name = {tool.name: tool for tool in tools}

def call_model(state: AgentState):
    # Bu düğümde print'e gerek yok, karmaşayı azaltır.
    llm = init_chat_model(model_name, model_provider="google_genai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def human_approval_node(state: AgentState):
    # Bu düğüm sadece ana thread tarafından çağrılacağı için input() güvenlidir.
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
        return {"messages": [AIMessage(content="Kullanıcı eylemi reddetti.")]}

def call_tool(state: AgentState):
    # Bu düğümde de print'e gerek yok.
    tool_call_message = next(msg for msg in reversed(state['messages']) if msg.tool_calls)
    tool_messages = []
    for tool_call in tool_call_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call['args'])
        tool_messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return {"messages": tool_messages}

# GÜNCELLEME: Tüm zekanın olduğu yer burası.
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    
    if not last_message.tool_calls:
        return "end"
    
    # Eğer eylem 'send_message' ise VE iş akışını bir KULLANICI başlattıysa, onaya git.
    if last_message.tool_calls[0]["name"] == "send_message" and state.get("invoked_by_user"):
        return "human_approval"
    else:
        # Aksi takdirde (başka bir araçsa VEYA otonom çalışıyorsa), doğrudan eyleme geç.
        return "action"
    
def after_approval(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if "Kullanıcı eylemi onayladı." in last_message.content:
        return "action"
    else:
        # Onay reddedildiğinde, ajanın durumu kullanıcıya bildirmesi için tekrar ajana dön.
        return "agent"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"human_approval": "human_approval", "action": "action", "end": END})
workflow.add_conditional_edges("human_approval", after_approval, {"action": "action", "agent": "agent"})
workflow.add_edge("action", "agent")

app = workflow.compile()