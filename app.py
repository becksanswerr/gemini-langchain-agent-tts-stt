# streamlit_app.py
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Yerel importlar
from agent_core import app
from config import SYSTEM_PROMPT
from database import save_conversation, get_conversations

st.set_page_config(page_title="Dynamic AI Agent", layout="wide")


# --- YARDIMCI FONKSİYONLAR ---
def run_agent(prompt):
    """Ajanı çalıştırır ve cevabını session_state'e ekler."""
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            # Ajanı mevcut konuşma geçmişiyle çalıştır
            inputs = {"messages": st.session_state.messages}
            result = app.invoke(inputs)
            bot_response = result["messages"][-1]
            st.session_state.messages.append(bot_response)
            st.rerun()

# --- OTURUM (SESSION) YÖNETİMİ ---
# Streamlit her etkileşimde scripti yeniden çalıştırdığı için,
# konuşma geçmişini `session_state` içinde saklamak ZORUNLUDUR.
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.messages = [AIMessage(content="Merhaba! Size nasıl yardımcı olabilirim?")]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- YAN PANEL (ADMIN PANEL) ---
with st.sidebar:
    st.header("Admin Paneli")
    st.write("Geçmiş Konuşmalar")
    
    # Veritabanından eski konuşmaları çek ve göster
    past_conversations = get_conversations()
    for conv in past_conversations:
        with st.expander(f"Konuşma ID: {conv['_id'][:8]}"):
            for msg in conv.get("messages", []):
                role = msg.get("type", "human")
                if role not in ["human", "ai", "assistant"]:
                    continue # Sadece insan ve ai mesajlarını göster
                with st.chat_message(role):
                    st.write(msg.get("content", ""))

# --- ANA SOHBET ARAYÜZÜ ---
st.title("🤖 Dynamic AI Agent")

# Mevcut konuşma geçmişini ekrana yazdır
for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# Kullanıcıdan yeni girdi al
if prompt := st.chat_input("Mesajınızı buraya yazın..."):
    # Kullanıcı mesajını geçmişe ve ekrana ekle
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ajanı çalıştır
    run_agent(prompt)
    
    # Her adımdan sonra konuşmayı veritabanına kaydet
    save_conversation(st.session_state.session_id, st.session_state.messages)