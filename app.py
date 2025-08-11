# streamlit_app.py

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from multiprocessing import freeze_support

# Yerel importlar
from agent_core import app
from config import SYSTEM_PROMPT
from database import save_conversation
# from tts_handler import initialize_tts_engine, generate_and_save_audio # TTS YORUM SATIRI

def main_app():
    st.set_page_config(page_title="Dynamic AI Agent", layout="wide")

    # --- ÖNBELLEKLEME (CACHING) - TTS YORUM SATIRI ---
    # @st.cache_resource
    # def get_tts_stream():
    #     return initialize_tts_engine()
    # tts_stream = get_tts_stream()

    # --- OTURUM (SESSION) YÖNETİMİ ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            AIMessage(content="Merhaba! Size nasıl yardımcı olabilirim?")
        ]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    st.title("🤖 Dynamic AI Agent")

    # --- MESAJLARI GÖSTERME DÖNGÜSÜ ---
    # Bu döngü, SADECE kullanıcıya gösterilmesi gereken mesajları filtreler.
    for message in st.session_state.messages:
        # Sistem mesajlarını ve içeriği olmayan AI mesajlarını atla
        if isinstance(message, SystemMessage) or (isinstance(message, AIMessage) and not message.content):
            continue
        
        # Araç mesajlarını özel işle: Sadece resim komutu olanları göster
        if isinstance(message, ToolMessage):
            if message.content.startswith("IMAGE_PATH:"):
                with st.chat_message("assistant"):
                    image_path = message.content.split(":")[1]
                    st.image(image_path)
            continue # Diğer tüm tool mesajlarını atla

        # İnsan ve AI mesajlarını göster
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(message.content)
            
    # --- KULLANICI GİRDİSİ VE AJAN ÇALIŞTIRMA MANTIĞI (YENİDEN YAZILDI) ---
    if prompt := st.chat_input("Mesajınızı buraya yazın..."):
        # 1. Kullanıcının mesajını geçici olarak geçmişe ekle
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        # 2. Ajanı çalıştır
        with st.spinner("Düşünüyor..."):
            inputs = {
                "messages": st.session_state.messages,
                "session_id": st.session_state.session_id
            }
            result = app.invoke(inputs)
            
            # 3. NİHAİ ÇÖZÜM: Session state'i, ajandan dönen nihai ve doğru
            #    geçmişle tamamen değiştir. Bu, tüm tekrar sorunlarını çözer.
            st.session_state.messages = result["messages"]

            # 4. Veritabanına kaydet
            save_conversation(st.session_state.session_id, st.session_state.messages)

            # --- TTS YORUM SATIRI ---
            # final_bot_response = st.session_state.messages[-1]
            # if isinstance(final_bot_response, AIMessage) and final_bot_response.content:
            #     audio_path = generate_and_save_audio(tts_stream, final_bot_response.content)
            #     if audio_path:
            #         st.session_state.audio_to_play = None # Sesi şimdilik oynatma

        # 5. Her şey bittikten sonra ekranı SADECE BİR KERE yenile
        st.rerun()

# --- ANA UYGULAMA GİRİŞ NOKTASI ---
if __name__ == '__main__':
    freeze_support()
    main_app()