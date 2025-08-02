import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Proje başlangıcında .env dosyasındaki değişkenleri yükle
load_dotenv()

# Ortam değişkenlerinden API anahtarını ve model adını güvenli bir şekilde al
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL_NAME")

# API anahtarının yüklenip yüklenmediğini kontrol et
if not api_key:
    raise ValueError("GOOGLE_API_KEY ortam değişkeni bulunamadı. Lütfen .env dosyanızı kontrol edin.")

# Model adı yoksa varsayılan bir model kullan
if not model_name:
    model_name = "gemini-pro"
    print("GEMINI_MODEL_NAME bulunamadı. Varsayılan olarak 'gemini-pro' kullanılacak.")

try:
    # Modeli .env'den okuduğumuz bilgilerle başlat
    llm = ChatGoogleGenerativeAI(model=model_name)

    print(f"'{model_name}' modeli başarıyla yüklendi. Bota mesajınızı yazabilirsiniz.")
    print("Çıkmak için 'q' veya 'quit' yazın.")

    while True:
        user_input = input("Siz: ")
        if user_input.lower() in ["q", "quit"]:
            print("Bot kapatılıyor. Hoşça kalın!")
            break

        # Modeli çağır ve yanıtı al
        response = llm.invoke(user_input)
        print(f"Bot: {response.content}")

except Exception as e:
    print(f"Bir hata oluştu: {e}")