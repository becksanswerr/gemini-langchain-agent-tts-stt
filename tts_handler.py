# tts_handler.py

import os
from RealtimeTTS import CoquiEngine, TextToAudioStream

AUDIO_OUTPUT_DIR = "audio_outputs"
OUTPUT_FILENAME = "response.wav"

def initialize_tts_engine():
    print("--- TTS Engine: Başlatılıyor (Bu mesajı sadece bir kere görmelisiniz)... ---")
    engine = CoquiEngine(
        voice="tts_models/tr/common-voice/vits",
        language="tr"
    )
    stream = TextToAudioStream(engine)
    return stream

def generate_and_save_audio(stream: TextToAudioStream, text: str):
    print("--- TTS: Ses üretimi başlıyor... ---")
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_OUTPUT_DIR, OUTPUT_FILENAME)
    
    try:
        stream.feed(text)
        stream.play(output_wavfile=output_path, muted=True)
        print(f"--- TTS: Ses başarıyla '{output_path}' dosyasına kaydedildi. ---")
        return output_path
    except Exception as e:
        print(f"--- HATA: TTS ses üretimi sırasında bir hata oluştu: {e} ---")
        return None