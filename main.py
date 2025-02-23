import streamlit as st
import whisper
import tempfile
import os
import json
import ffmpeg
import torch
from whisper.utils import get_writer

# Streamlit sayfa konfigürasyonu en üstte olmalı
st.set_page_config(page_title="Whisper Ses Transkripsiyon", layout="centered")

# GPU Bellek Optimizasyonu ve # CUDA Optimizasyonları
torch.cuda.empty_cache()  # Kullanılmayan GPU belleğini boşalt
torch.backends.cudnn.benchmark = True  # CUDA optimizasyonları
torch.backends.cudnn.deterministic = False
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# GPU Kullanımı Gösterimi
st.sidebar.header("📊 GPU Kullanımı")
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated() / 1024**3
    reserved = torch.cuda.memory_reserved() / 1024**3
else:
    allocated, reserved = 0, 0

st.sidebar.write(f"💾 Ayrılmış Bellek: {allocated:.2f} GB")
st.sidebar.write(f"🔒 Rezerve Edilen Bellek: {reserved:.2f} GB")

st.title("🎙️ Ses veya Video Dosyası Yükleyin ve Metne Çevirin")

# Model seçenekleri
model_options = {
    "tiny": {
        "parameters": "39M",
        "VRAM": "~1 GB",
        "speed": "~10x (En hızlı)",
        "accuracy": "Düşük doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil)",
        "description": "Tiny modeli en hafif ve en hızlı modeldir. Mobil cihazlar ve düşük donanımlı sistemler için uygundur. Ancak doğruluğu düşüktür. Türkçe dahil birçok dili destekler ancak hata oranı yüksektir.",
    },
    "base": {
        "parameters": "74M",
        "VRAM": "~1 GB",
        "speed": "~7x",
        "accuracy": "Orta düzey doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil)",
        "description": "Base modeli, hafif ama daha doğru bir modeldir. Gerçek zamanlı transkripsiyon için uygundur. Türkçe dahil birçok dili destekler ancak büyük modellere göre daha fazla hata yapabilir.",
    },
    "small": {
        "parameters": "244M",
        "VRAM": "~2 GB",
        "speed": "~4x",
        "accuracy": "İyi doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil)",
        "description": "Small modeli, düşük gecikmeli ses işleme ve orta seviye doğruluk isteyen kullanıcılar için idealdir. Türkçe transkripsiyon performansı iyidir ancak hala büyük modeller kadar güçlü değildir.",
    },
    "medium": {
        "parameters": "769M",
        "VRAM": "~5 GB",
        "speed": "~2x",
        "accuracy": "Yüksek doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil)",
        "description": "Medium modeli, profesyonel transkripsiyon işleri için uygundur. Türkçe dahil birçok dilde yüksek doğruluk sunar. Ancak büyük modellere göre daha az detaylı transkripsiyon yapabilir.",
    }
}

# Model seçimi
selected_model = st.selectbox("Kullanmak istediğiniz modeli seçin:", list(model_options.keys()))

# Seçilen modele göre açıklamaları göster
model_info = model_options[selected_model]
torch.cuda.synchronize()  # GPU işlemlerini senkronize et

st.subheader(f"📌 Seçilen Model: {selected_model.upper()}")
st.write(f"**Parametre Sayısı:** {model_info['parameters']}")
st.write(f"**Gerekli VRAM:** {model_info['VRAM']}")
st.write(f"**Hız:** {model_info['speed']}")
st.write(f"**Doğruluk:** {model_info['accuracy']}")
st.write(f"**Dil Desteği:** {model_info['languages']}")  # 🌍 Dil desteğini ekledik!
st.write(f"**Açıklama:** {model_info['description']}")

# Ses dosyasını WAV formatına dönüştürme fonksiyonu
def convert_to_wav(input_path):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format="wav", acodec="pcm_s16le", ac=1, ar="16000")
            .run(quiet=True, overwrite_output=True)
        )
        return output_path
    except Exception as e:
        st.error(f"⚠️ Ses dönüştürme hatası: {e}")
        return None

# Whisper modelini yükleme
@st.cache_resource
def load_whisper_model(model_name):
    return whisper.load_model(model_name, device="cuda", download_root="models/")

whisper_model = load_whisper_model(selected_model)

uploaded_file = st.file_uploader(
    "Bir ses veya video dosyası yükleyin (MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC)",
    type=["mp3", "wav", "mp4", "m4a", "ogg", "caf", "aac", "flac"]
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    # Geçici dosya oluştur
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
    temp_audio_file.write(uploaded_file.read())
    temp_audio_file.close()

    # WAV formatına çevir
    wav_filename = convert_to_wav(temp_audio_file.name)

    # Eski dosyayı sil
    os.remove(temp_audio_file.name)

    if wav_filename:
        st.write("🔄 Ses dosyanız işleniyor, lütfen bekleyin...")

        # GPU kullanarak transkripsiyon işlemi
        result = whisper_model.transcribe(wav_filename, fp16=True)

        # Dönüştürülen WAV dosyasını sil
        os.remove(wav_filename)
        
        if "text" in result:
            transcribed_text = result["text"]
            segments = result["segments"]
            
            st.subheader("📝 Transkripsiyon Sonucu")
            st.text_area("Çıktı:", transcribed_text, height=250)
            
            json_output = json.dumps(segments, ensure_ascii=False, indent=4)
            st.download_button("📥 JSON Formatında İndir", json_output, file_name="transcription.json", mime="application/json")
            
            # SRT formatına çevirme
            srt_writer = get_writer("srt", ".")
            srt_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".srt").name
            srt_writer(result, srt_filename)
            
            with open(srt_filename, "r", encoding="utf-8") as file:
                srt_content = file.read()
            os.remove(srt_filename)
            
            st.download_button("📥 Düz Metni İndir", transcribed_text, file_name="transcription.txt", mime="text/plain")
            st.download_button("📥 Zaman Damgalı Altyazı (SRT) İndir", srt_content, file_name="transcription.srt", mime="text/plain")