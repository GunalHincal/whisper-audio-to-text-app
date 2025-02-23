# STREAMLIT UYGULAMASI 
import streamlit as st
import whisper
import os
import ffmpeg
import json
from tempfile import NamedTemporaryFile
from whisper.utils import get_writer

# 📌 Whisper Model Seçenekleri ve Açıklamalar
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
    },
    "large": {
        "parameters": "1550M",
        "VRAM": "~10 GB",
        "speed": "1x (En yavaş)",
        "accuracy": "Çok yüksek doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil, en yüksek doğrulukta)",
        "description": "Large modeli, en yüksek doğruluğa sahiptir. Türkçe de dahil olmak üzere tüm desteklenen dillerde en iyi sonuçları verir. Büyük projeler ve akademik çalışmalar için uygundur.",
    },
    "turbo": {
        "parameters": "809M",
        "VRAM": "~6 GB",
        "speed": "~8x",
        "accuracy": "Large modeline yakın doğruluk",
        "languages": "🌍 Çok dilli (Türkçe dahil, hızlı transkripsiyon)",
        "description": "Turbo modeli, Large modeline göre daha hızlıdır ama doğrulukta hafif bir düşüş olabilir. Türkçe dahil tüm dilleri destekler ve özellikle hız gerektiren durumlar için uygundur.",
    },
}

# 🎯 Streamlit Arayüzü
st.set_page_config(page_title="Whisper Ses Transkripsiyon", layout="centered")
st.title("🎙️ Ses Dosyası Yükleyin ve Metne Çevirin")

# 📌 Kullanıcıya Model Seçimi Sun
selected_model = st.selectbox("Kullanmak istediğiniz modeli seçin:", list(model_options.keys()))

# 📌 Whisper Modelini Önbelleğe Al
@st.cache_resource
def load_whisper_model(model_name):
    return whisper.load_model(model_name, download_root="models/")

# Seçilen model yükleniyor (Önbellekten çağrılır)
whisper_model = load_whisper_model(selected_model)

# Seçilen modele göre açıklamaları göster
model_info = model_options[selected_model]

st.subheader(f"📌 Seçilen Model: {selected_model.upper()}")
st.write(f"**Parametre Sayısı:** {model_info['parameters']}")
st.write(f"**Gerekli VRAM:** {model_info['VRAM']}")
st.write(f"**Hız:** {model_info['speed']}")
st.write(f"**Doğruluk:** {model_info['accuracy']}")
st.write(f"**Dil Desteği:** {model_info['languages']}")  # 🌍 Dil desteğini ekledik!
st.write(f"**Açıklama:** {model_info['description']}")

# 📥 Ses Dosyası Yükleme
uploaded_file = st.file_uploader(
    "Bir ses dosyası yükleyin (MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC vb.)", 
    type=["mp3", "wav", "mp4", "m4a", "ogg", "caf", "aac", "flac"]
)

def convert_to_wav(input_file):
    """ Ses dosyasını WAV formatına çevirir. """
    output_file = "converted_audio.wav"
    try:
        ffmpeg.input(input_file).output(output_file, format="wav").run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return output_file
    except Exception as e:
        st.error(f"⚠️ FFmpeg Dönüştürme Hatası: {e}")
        return None

def transcribe_audio(audio_file, model):
    """ Önbelleğe alınmış Whisper modeli ile transkripsiyon yapar. """
    result = model.transcribe(audio_file)
    return result  # JSON formatında döndür

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")

    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_filename = temp_file.name
    
    # Ses dosyasını WAV formatına dönüştür
    wav_filename = convert_to_wav(temp_filename)
    
    if wav_filename:
        st.write("🔄 Ses dosyanız işleniyor, lütfen bekleyin...")

        # Önbelleğe alınmış modeli kullanarak transkripsiyon yap
        result = transcribe_audio(wav_filename, whisper_model)

        if "text" in result and "segments" in result:
            transcribed_text = result["text"]  # Düz metin transkripsiyonu
            segments = result["segments"]  # Zaman damgalı segmentler

            os.remove(wav_filename)  # Geçici dosyayı temizle
            os.remove(temp_filename)  # Orijinal dosyayı temizle

            st.subheader("📝 Transkripsiyon Sonucu")
            st.text_area("Çıktı:", transcribed_text, height=250)

            # Zaman damgalı transkripsiyonu JSON formatında kaydet
            json_output = json.dumps(segments, ensure_ascii=False, indent=4)

            # **SRT formatına çevirmek için get_writer kullanımı**
            srt_writer = get_writer("srt", ".")
            srt_filename = "transcription.srt"
            srt_writer(result, srt_filename, {"max_line_width": 50, "max_line_count": 2, "highlight_words": False})

            # 📥 **İndirme Butonları**
            st.download_button("📥 Düz Metni İndir", transcribed_text, file_name="transcription.txt", mime="text/plain")
            st.download_button("📥 Zaman Damgalı JSON İndir", json_output, file_name="transcription.json", mime="application/json")
            
            # SRT dosyasını oku ve indirme butonu oluştur
            with open(srt_filename, "r", encoding="utf-8") as file:
                srt_content = file.read()
            st.download_button("📥 Zaman Damgalı Altyazı (SRT) İndir", srt_content, file_name="transcription.srt", mime="text/plain")
        else:
            st.error("⚠️ Transkripsiyon başarısız! Lütfen başka bir ses dosyası deneyin.")