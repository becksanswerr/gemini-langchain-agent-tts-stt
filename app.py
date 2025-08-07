# streamlit_app.py
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from multiprocessing import freeze_support

from agent_core import app
from config import SYSTEM_PROMPT
from database import save_conversation, get_conversations
from tts_handler import initialize_tts_engine, generate_and_save_audio

def main_app():
    st.set_page_config(page_title="Voice AI Agent", layout="wide")

    # --- ÖNBELLEKLEME (CACHING) ---
    #@st.cache_resource
    #def get_tts_stream():
    #    return initialize_tts_engine()
    #tts_stream = get_tts_stream()


    # --- YARDIMCI FONKSİYONLAR ---
    def run_agent(prompt):
        """Ajanı çalıştırır, cevabını ve eylemlerini gösterir."""
        with st.chat_message("assistant"):
            final_bot_response = None
            with st.spinner("Düşünüyor..."):
                inputs = {"messages": st.session_state.messages}

                result = app.invoke(inputs)
                final_bot_response = result["messages"][-1]
                st.session_state.messages.append(final_bot_response)

                # Şeffaflık katmanı
                tool_calls = [msg.tool_calls for msg in result["messages"] if hasattr(msg, "tool_calls") and msg.tool_calls]
                if tool_calls:
                    with st.expander("🤖 Ajanın Eylemleri"):
                        # tool_calls listesi içindeki listeyi düzleştir
                        all_calls = [item for sublist in tool_calls for item in sublist]
                        for tool_call in all_calls:
                            st.markdown(f"**Araç:** `{tool_call['name']}`")
                            st.markdown(f"**Parametreler:** `{tool_call['args']}`")

            # GÜNCELLEME: TTS sadece her şey bittikten sonra, nihai cevap için çağrılır
            #if final_bot_response:
            #    audio_path = generate_and_save_audio(tts_stream, final_bot_response.content)
            #    if audio_path:
            #        st.session_state.audio_to_play = audio_path
#
            st.rerun()

    # --- OTURUM (SESSION) YÖNETİMİ ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            AIMessage(content="Merhaba! Size nasıl yardımcı olabilirim?")
        ]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "audio_to_play" not in st.session_state:
        st.session_state.audio_to_play = None


    # --- YAN PANEL ve ANA SOHBET ARAYÜZÜ ---
    with st.sidebar:
        st.header("Admin Paneli")
        st.write("Geçmiş Konuşmalar")
        
        past_conversations = get_conversations()
        for conv in past_conversations:
            with st.expander(f"Konuşma ID: {conv['_id'][:8]}"):
                for msg in conv.get("messages", []):
                    role = msg.get("type", "human")
                    if role not in ["human", "ai", "assistant"]:
                        continue
                    with st.chat_message(role):
                        st.write(msg.get("content", ""))

    st.title("🤖 Voice AI Agent")

    for message in st.session_state.messages:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(message.content)

    if st.session_state.audio_to_play:
        st.audio(st.session_state.audio_to_play, autoplay=True)
        st.session_state.audio_to_play = None

    if prompt := st.chat_input("Mesajınızı buraya yazın..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        run_agent(prompt)
        save_conversation(st.session_state.session_id, st.session_state.messages)


# --- ANA UYGULAMA GİRİŞ NOKTASI ---
if __name__ == '__main__':
    freeze_support()
    main_app()