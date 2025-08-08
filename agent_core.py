# agent_core.py 

import os
import operator
import tts_handler
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from config import SYSTEM_PROMPT
from tools.custom_tools import  get_landoflegends_events, get_current_time, get_hotel_info, get_park_units

load_dotenv()
model_name = os.getenv("GEMINI_MODEL_NAME")

def get_tools():
    """İhtiyaç duyulduğunda araçları oluşturur ve döndürür."""
    #tavily_tool = TavilySearch(
    #    max_results=3, 
    #    tavily_api_key = os.getenv("TAVILY_API_KEY")
    #)
    return [
        #tavily_tool, 
        get_current_time,
        get_landoflegends_events, 
        get_park_units,
        get_hotel_info
    ]



class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def call_model(state: AgentState):
    tools = get_tools() 
    llm = init_chat_model(model_name, model_provider="google_genai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def call_tool(state: AgentState):
    tools = get_tools()
    tools_by_name = {tool.name: tool for tool in tools}
    
    tool_call_message = next(msg for msg in reversed(state['messages']) if msg.tool_calls)
    tool_messages = []
    
    for tool_call in tool_call_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        
        try:
            observation = tool.invoke(tool_call['args'])
            
            if isinstance(observation, list):
                formatted_observation = "İnternet aramasından şu sonuçlar bulundu:\n\n"
                for i, item in enumerate(observation):
                    snippet = item.get('content', 'İçerik bulunamadı.')
                    formatted_observation += f"{i+1}. {snippet}\n\n"
            else:
                formatted_observation = str(observation)

        except Exception as e:
            formatted_observation = f"'{tool.name}' aracı çalıştırılırken bir hata oluştu: {e}"
            
        tool_messages.append(ToolMessage(content=formatted_observation, tool_call_id=tool_call["id"]))
        
    return {"messages": tool_messages}

def should_continue(state: AgentState) -> str:
    if not state["messages"][-1].tool_calls:
        return "end"
    else:
        return "action"

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"action": "action", "end": END})
workflow.add_edge("action", "agent")

app = workflow.compile()