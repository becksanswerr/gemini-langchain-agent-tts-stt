# debug_agent.py

import os # os modülünü import et
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

# 1. Her şeyden önce .env dosyasını yükle
# override=True: Eğer sistemde başka bir anahtar varsa bile, .env'deki anahtarı kullanmaya zorla.
load_dotenv(override=True)

# 2. API Anahtarını DOĞRUDAN OKU ve KONTROL ET
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY .env dosyasında bulunamadı veya okunamadı. Lütfen kontrol edin.")
else:
    print(f"--- Tavily API Anahtarı başarıyla bulundu: tvly-******{tavily_api_key[-4:]} ---")


# 3. LLM'i başlat.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 4. Araçları tanımla ve API anahtarını DOĞRUDAN VER
tools = [TavilySearch(max_results=3, tavily_api_key=tavily_api_key)]

# 5. Standart ReAct Prompt'unu çek.
prompt = hub.pull("hwchase17/react")

# 6. Ajanı oluştur.
agent = create_react_agent(llm, tools, prompt)

# 7. AgentExecutor'ı oluştur.
# handle_parsing_errors=True: Ajanın kafası karışırsa, hatayı sana göstermeden önce tekrar denemesini sağlar.
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# 8. Ajanı test sorusuyla çalıştır.
print("\n--- NİHAİ AJAN TESTİ BAŞLATILIYOR ---")
soru = "elon musk kimdir"
print(f"Soru: {soru}")

try:
    response = agent_executor.invoke({"input": soru})
    print("\n--- TEST BAŞARILI ---")
    print("Ajanın Nihai Cevabı:")
    print(response["output"])

except Exception as e:
    print("\n--- TEST BAŞARISIZ ---")
    print(f"Bir hata oluştu: {e}")