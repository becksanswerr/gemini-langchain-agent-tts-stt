# streamlit_app.py

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
import base64
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from multiprocessing import freeze_support

# Yerel importlar
from agent_core import app
from config import SYSTEM_PROMPT
from database import save_conversation

# YENİ: İki sütunlu ve daha hedefli bir stil için fonksiyon
def set_page_style():
    with open("pictures/land_of_legends_banner.png", "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()

    # CSS stilleri
    page_style = f"""
        <style>
        /* Ana uygulama arka planı */
        .stApp {{
            background-color: #0E0017; /* Arka planda resim yerine koyu bir renk */
        }}

        /* Streamlit'in varsayılan elemanlarını gizle */
        #MainMenu, footer, header {{
            visibility: hidden;
        }}

        /* GÜNCELLEME: Sağdaki sohbet sütununu hedef alıyoruz */
        /* [data-testid="column"] Streamlit'in sütunları için kullandığı bir etikettir */
        [data-testid="column"]:nth-of-type(2) > div {{
            background-color: rgba(10, 5, 20, 0.85); /* Hafif morumsu, yarı saydam siyah */
            backdrop-filter: blur(5px);
            border-radius: 15px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            height: 95vh; /* Ekranın yüksekliğine yakın bir yükseklik */
            overflow-y: auto; /* Mesajlar sığmazsa kaydırma çubuğu çıksın */
        }}
        
        /* Sohbet mesajlarının kendi arka planı */
        .stChatMessage {{
            background-color: rgba(255, 255, 255, 0.08);
            border-radius: 10px;
        }}
        </style>
    """
    st.markdown(page_style, unsafe_allow_html=True)

# --- ANA UYGULAMA FONKSİYONU ---
def main_app():
    st.set_page_config(
        page_title="Landy", 
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    set_page_style()

    # --- OTURUM YÖNETİMİ ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            AIMessage(content="Ben Landy. The Land of Legends'taki dijital asistanınız. Size nasıl yardımcı olabilirim?")
        ]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # --- İKİ SÜTUNLU YAPI ---
    left_col, right_col = st.columns((2, 3)) # Sol sütun daha dar, sağ sütun daha geniş

    # --- SOL SÜTUN: GÖRSEL PANEL ---
    with left_col:
        st.image("pictures/land_of_legends_banner.png")
        st.title("🤖 Landy")
        st.caption("The Land of Legends'a Hoş Geldiniz! Etkinlikler, üniteler, oteller veya biletler hakkında her şeyi bana sorabilirsiniz.")

    # --- SAĞ SÜTUN: SOHBET PANELİ ---
    with right_col:
        # Mesajları gösterme
        for message in st.session_state.messages:
            if isinstance(message, SystemMessage): continue
            
            if isinstance(message, HumanMessage):
                with st.chat_message("user", avatar="pictures/user_avatar.png"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                if not message.content: continue
                with st.chat_message("assistant", avatar="pictures/bot_avatar.png"):
                    st.markdown(message.content)
            elif isinstance(message, ToolMessage):
                if message.content.startswith("IMAGE_PATH:"):
                    with st.chat_message("assistant", avatar="pictures/bot_avatar.png"):
                        image_path = message.content.split(":")[1]
                        st.image(image_path)
                continue

    # --- KULLANICI GİRDİSİ (Sütunların Dışında, Sayfanın Altında) ---
    if prompt := st.chat_input("Landy'a bir soru sorun..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        with st.spinner("Landy düşünüyor..."):
            inputs = {
                "messages": st.session_state.messages,
                "session_id": st.session_state.session_id
            }
            result = app.invoke(inputs)
            st.session_state.messages = result["messages"]
            save_conversation(st.session_state.session_id, st.session_state.messages)

        st.rerun()

# --- ANA GİRİŞ NOKTASI ---
if __name__ == '__main__':
    freeze_support()
    main_app()