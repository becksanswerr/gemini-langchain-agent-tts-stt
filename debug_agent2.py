# debug_agent.py - SON VE NİHAİ VERSİYON (ÖZEL PROMPT İLE)

import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate # YENİ: Kendi prompt'umuzu oluşturmak için

# --- ANAHTAR YÜKLEME ---
# Bu bölümün doğru çalıştığını biliyoruz, sadeleştirebiliriz.
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not google_api_key or not tavily_api_key:
    raise ValueError("Lütfen .env dosyanızda GOOGLE_API_KEY ve TAVILY_API_KEY'in olduğundan emin olun.")

print("--- Tüm API Anahtarları başarıyla yüklendi. ---")


# YENİ: Kendi özel ReAct prompt'umuzu oluşturuyoruz.
# Bu, ajana nasıl düşüneceğini ve davranacağını söyleyen talimat setidir.
TURKISH_REACT_PROMPT_TEMPLATE = """
Sen, sana verilen araçları kullanarak soruları cevaplayan büyük bir dil modelisin.

Sana sunulan araçlar şunlardır:
{tools}

Şu formatı kullan:

Question: Cevaplaman gereken soru.
Thought: Ne yapman gerektiğini her zaman düşünmelisin.
Action: Kullanacağın aracın adı, [{tool_names}] listesinden biri olmalı.
Action Input: Araca vereceğin girdi.
Observation: Aracın sana döndürdüğü sonuç.
... (Bu Thought/Action/Action Input/Observation döngüsü birkaç kez tekrarlanabilir)
Thought: Artık nihai cevabı biliyorum.
Final Answer: Sorunun orijinal dilinde, kapsamlı ve açıklayıcı nihai cevap.

ÖNEMLİ KURALLAR:
1. Bir aracı kullandıktan sonra dönen 'Observation' sonucunu analiz et.
2. Eğer bu bilgi cevabı oluşturmak için yeterliyse, başka bir araca gerek duymadan kendi bilgini ve muhakeme yeteneğini kullanarak bir 'Final Answer' üret.
3. Sen büyük bir dil modelisin; özetleme, analiz etme ve **çeviri yapma** gibi görevleri bir araç kullanmadan kendin yapabilirsin.
4. **Nihai cevabın (Final Answer), sorunun sorulduğu dilde (Türkçe) olmalıdır.**

Hadi başlayalım!

Question: {input}
Thought: {agent_scratchpad}
"""

# --- AJAN KURULUMU ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=google_api_key)
    tools = [TavilySearch(max_results=2, tavily_api_key=tavily_api_key)]

    # Yeni ve özel prompt'umuzu kullanarak prompt nesnesini oluşturuyoruz.
    prompt = PromptTemplate.from_template(TURKISH_REACT_PROMPT_TEMPLATE)

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    print("\n--- ÖZEL PROMPT İLE AJAN TESTİ BAŞLATILIYOR ---")
    soru = "rixosun sahibi kimdirr"
    print(f"Soru: {soru}")

    response = agent_executor.invoke({"input": soru})
    
    print("\n--- TEST BAŞARILI ---")
    print("Ajanın Nihai Cevabı:")
    print(response["output"])

except Exception as e:
    print("\n--- TEST BAŞARISIZ ---")
    print(f"Bir hata oluştu: {e}")