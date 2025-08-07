# api_test_units.py

import requests
import json
import html

API_URL = "https://www.thelandoflegends.com/en/api/unex-list"

def test_units_api():
    """The Land of Legends ünite API'sini test eder."""
    print(f"API'ye istek gönderiliyor: {API_URL}")
    
    try:
        response = requests.get(API_URL, timeout=10)
        
        print("\nHTTP Status Kodu:", response.status_code)
        
        # API bazen 200 OK durum koduyla bile boş veya hatalı cevap verebilir.
        # Bu yüzden raise_for_status'tan önce içeriği kontrol edelim.
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n--- GELEN HAM VERİ ---")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                if not data:
                    print("\nSONUÇ: API başarılı bir şekilde bağlandı ancak boş bir liste döndürdü.")
            except json.JSONDecodeError:
                print("\nSONUŞ: API başarılı bir şekilde bağlandı ancak geçerli bir JSON döndürmedi. Ham cevap:")
                print(response.text)
        else:
            print("\nHATA: API başarılı olmayan bir durum kodu döndürdü.")
            response.raise_for_status()


    except requests.exceptions.RequestException as e:
        print(f"\nAPI İsteği Sırasında Bir Hata Oluştu: {e}")

if __name__ == "__main__":
    test_units_api()