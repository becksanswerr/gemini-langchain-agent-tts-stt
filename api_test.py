# api_test.py

import requests
import json


API_URL = "mmmmmmmmmm"

def test_landoflegends_api():
    """
    The Land of Legends etkinlik API'sini test eder ve gelen ham veriyi yazdırır.
    """
    print(f"API'ye istek gönderiliyor: {API_URL}")
    
    try:
        response = requests.get(API_URL, timeout=10)
    
        response.raise_for_status()
        
        print("\nİstek başarılı! HTTP Status Kodu:", response.status_code)

        data = response.json()
        
        print("\n--- GELEN HAM VERİ ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if isinstance(data, list) and len(data) > 0:
            print("\n--- VERİ ANALİZİ ---")
            print(f"Toplam {len(data)} etkinlik bulundu.")
            first_event = data[0]
            title = first_event.get('title')
            description = first_event.get('description')
            print(f"İlk etkinliğin başlığı: {title} (Tip: {type(title)})")
            print(f"İlk etkinliğin açıklaması: {description} (Tip: {type(description)})")
            if title is None:
                print("\nSONUÇ: API düzgün çalışıyor ancak etkinlik detayları (başlık vb.) şu anda boş (null) olarak gönderiliyor.")

    except requests.exceptions.HTTPError as http_err:
        print(f"\nHTTP Hatası Oluştu: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"\nAPI İsteği Sırasında Bir Hata Oluştu: {req_err}")
    except json.JSONDecodeError:
        print("\nAPI'den gelen cevap JSON formatında değil. Ham cevap:")
        print(response.text)

if __name__ == "__main__":
    test_landoflegends_api()