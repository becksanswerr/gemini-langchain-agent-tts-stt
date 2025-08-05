# tools/custom_tools.py

import os
import requests
import html
from datetime import datetime 
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

lol_api = os.getenv("LAND_OF_LEGENDS_API_KEY")

@tool
def get_current_time():
    """Şu anki tam tarihi ve saati almak için kullanılır. 
    Kullanıcı 'bugün', 'yarın', 'saat kaç', 'hangi gündeyiz' gibi zamanla ilgili 
    sorular sorduğunda veya bir etkinliğin bugüne göre durumunu değerlendirmek 
    gerektiğinde bu araç çağrılmalıdır."""
    
    print("--- ARAÇ: Mevcut zaman alınıyor... ---")
    now = datetime.now()
    return now.strftime("%A, %d %B %Y, %H:%M")




@tool
def get_landoflegends_events():
    """The Land of Legends tema parkındaki güncel ve gelecek etkinlikleri listelemek için kullanılır. 
    Kullanıcı 'Land of Legends', 'tema parkı' veya oradaki 'etkinlikler', 'konserler', 'gösteriler' 
    hakkında soru sorduğunda bu araç çağrılmalıdır."""
    
    print("--- ARAÇ: Land of Legends etkinlikleri API'si çağrılıyor... ---")
    try:
        response = requests.get(lol_api, timeout=10)
        response.raise_for_status()
        
        events = response.json()
        
        if not events:
            return "Şu anda The Land of Legends'ta planlanmış bir etkinlik bulunmuyor."
        
        formatted_events = "The Land of Legends'taki güncel etkinlikler şunlardır:\n\n"
        for event in events:
            title = event.get('event_name', 'Başlık Yok')
            
            raw_description = event.get('event_desc', 'Açıklama Yok')
            description = html.unescape(raw_description).strip()
            
            times = event.get('event_time_', [])
            times_str = ", ".join(times) if times else "Belirtilmemiş"
            
            formatted_events += f"🔹 ETKİNLİK: {title}\n"
            if description: 
                formatted_events += f"   Açıklama: {description}\n"
            formatted_events += f"   Zamanlar: {times_str}\n\n"
        
        return formatted_events

    except requests.RequestException as e:
        print(f"--- HATA: API isteği başarısız: {e} ---")
        return f"Etkinlik bilgileri alınırken bir hata oluştu: {e}"


