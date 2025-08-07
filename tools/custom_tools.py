# tools/custom_tools.py

import os
import requests
import html
from datetime import datetime 
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

lol_event_api = os.getenv("LAND_OF_LEGENDS_EVENT_API")
lol_unit_api = os.getenv("LAND_OF_LEGENDS_UNIT_API")
lol_hotel_api = os.getenv("LAND_OF_LEGENDS_HOTEL_API")

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
def get_park_units():
    """The Land of Legends tema parkındaki üniteleri (kaydıraklar, atraksiyonlar, roller coaster'lar vb.), 
    özelliklerini ve özellikle yaş/boy gibi kısıtlamalarını listelemek için kullanılır."""
    
    print("--- ARAÇ: Park Üniteleri API'si çağrılıyor (GELİŞMİŞ VERSİYON)... ---")
    url = "https://www.thelandoflegends.com/en/api/unex-list"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        units_data = response.json()
        
        if not units_data:
            return "Şu anda parktaki üniteler hakkında bilgi alınamıyor."
        
        final_output = "The Land of Legends'taki üniteler ve özellikleri:\n\n"
        
        # GÜNCELLEME: API'den gelen sözlüğün her bir park bölümünü geziyoruz.
        for park_name, units in units_data.items():
            final_output += f"--- {park_name} Bölümü ---\n"
            for unit in units:
                # HTML temizliği için bir yardımcı fonksiyon
                def clean_html(raw_html):
                    if not raw_html: return ""
                    return BeautifulSoup(raw_html, "html.parser").get_text(strip=True)

                name = unit.get('unex_name', 'İsim Yok')
                description = clean_html(unit.get('unex_text', ''))
                
                final_output += f"🎢 Ünite: {name}\n"
                if description:
                    final_output += f"   Açıklama: {description}\n"
                
                # GÜNCELLEME: İç içe geçmiş 'unex_spec_' sözlüğünden kısıtlamaları alıyoruz.
                specs = unit.get('unex_spec_', {})
                min_height_spec = specs.get('min_height', {})
                min_height = min_height_spec.get('value') if min_height_spec else None
                
                min_height_parent_spec = specs.get('min_height_with_parent', {})
                min_height_parent = min_height_parent_spec.get('value') if min_height_parent_spec else None

                if min_height:
                    final_output += f"   Minimum Boy: {min_height} cm\n"
                if min_height_parent:
                    final_output += f"   Ebeveyn ile Minimum Boy: {min_height_parent} cm\n"
                
                final_output += "\n"

        return final_output

    except requests.RequestException as e:
        return f"Park üniteleri bilgisi alınırken bir hata oluştu: {e}"

@tool
def get_hotel_info():
    """The Land of Legends'taki otel, konaklama seçenekleri, otel misafirlerine özel ayrıcalıklar (privileges), 
    teklifler (offers) ve indirimler (discounts) hakkında detaylı bilgi almak için kullanılır."""
    
    print("--- ARAÇ: Otel Bilgileri API'si çağrılıyor (GELİŞMİŞ VERSİYON)... ---")
    url = "***REMOVED***"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        hotels_data = response.json()
        
        if not hotels_data:
            return "Şu anda otel bilgileri alınamıyor."
            
        final_output = "The Land of Legends'taki konaklama bilgileri, ayrıcalıklar ve teklifler:\n\n"
        
        for hotel in hotels_data:
            # HTML etiketlerini temizlemek için bir yardımcı fonksiyon
            def clean_html(raw_html):
                if not raw_html: return ""
                return BeautifulSoup(raw_html, "html.parser").get_text(separator="\n", strip=True)

            name = hotel.get('hotel_name', 'İsim Yok')
            description = clean_html(hotel.get('hotel_description', ''))
            
            final_output += f"🏨 OTEL: {name}\n"
            if description:
                final_output += f"   Açıklama: {description}\n"

            # Ayrıcalıkları (Privileges) işle
            privileges = hotel.get('hotel_previlige_', [])
            if privileges:
                final_output += "   AYRICALIKLAR:\n"
                for priv in privileges:
                    priv_name = priv.get('name', 'Ayrıcalık Adı Yok')
                    priv_desc = clean_html(priv.get('description', ''))
                    final_output += f"     - {priv_name}: {priv_desc}\n"

            # Teklifleri ve İndirimleri (Offers) işle
            offers = hotel.get('hotel_offer_', [])
            if offers:
                final_output += "   TEKLİFLER VE İNDİRİMLER:\n"
                for offer in offers:
                    offer_name = offer.get('name', 'Teklif Adı Yok')
                    offer_desc = clean_html(offer.get('description', ''))
                    final_output += f"     - {offer_name}: {offer_desc}\n"
            
            final_output += "\n" + "-"*20 + "\n\n"

        return final_output
    except requests.RequestException as e:
        return f"Otel bilgileri alınırken bir hata oluştu: {e}"




@tool
def get_landoflegends_events():
    """The Land of Legends tema parkındaki güncel ve gelecek etkinlikleri listelemek için kullanılır. 
    Kullanıcı 'Land of Legends', 'tema parkı' veya oradaki 'etkinlikler', 'konserler', 'gösteriler' 
    hakkında soru sorduğunda bu araç çağrılmalıdır."""
    
    print("--- ARAÇ: Land of Legends etkinlikleri API'si çağrılıyor... ---")
    try:
        response = requests.get(lol_event_api, timeout=10)
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


