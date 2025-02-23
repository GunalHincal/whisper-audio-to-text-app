# STREAMLIT UYGULAMASI

import streamlit as st
import whisper
import tempfile
import os
import os
import json
import ffmpeg
import time
from whisper.utils import get_writer
import torch
torch.cuda.empty_cache()  # Boşta kalan GPU belleğini temizle
torch.backends.cudnn.benchmark = True  # CUDA optimizasyonlarını aç
torch.backends.cudnn.deterministic = False  # GPU kullanımı için esneklik sağlar

# 🛠 CUDA Optimizasyonları
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
torch.cuda.empty_cache()  # Boşta kalan GPU belleğini temizle
torch.backends.cudnn.benchmark = True  # CUDA optimizasyonlarını aç
torch.backends.cudnn.deterministic = False  # GPU kullanımı için esneklik sağlar

# 📊 GPU Kullanımını Gösteren Fonksiyon
def get_gpu_usage():
    allocated = torch.cuda.memory_allocated() / 1024**3
    reserved = torch.cuda.memory_reserved() / 1024**3
    return allocated, reserved

# 🏗️ Sayfa Yapılandırmasını En Üste Koy!
st.set_page_config(page_title="Whisper Ses Transkripsiyon", layout="centered")

# 🎯 GPU Kullanımını Sidebar'da Göster
st.sidebar.header("📊 GPU Kullanımı")
allocated, reserved = get_gpu_usage()
st.sidebar.write(f"💾 Ayrılmış Bellek: {allocated:.2f} GB")
st.sidebar.write(f"🔒 Rezerve Edilen Bellek: {reserved:.2f} GB")

st.title("🎙️ Ses veya Video Dosyası Yükleyin ve Metne Çevirin")

# 📌 Ses Dönüştürme Fonksiyonu
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

# 📌 Transkripsiyon Fonksiyonu
def transcribe_audio(audio_path, model):
    result = model.transcribe(audio_path, fp16=False)
    return result

# 📌 Geçici Dosya Temizleme Fonksiyonu
def clear_temp_files():
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path):
                time.sleep(1)
                os.remove(file_path)
        except PermissionError:
            print(f"Dosya kullanımda, daha sonra silmeyi deneyin: {file_path}")
        except Exception as e:
            print(f"Dosya silinirken hata oluştu: {e}")

# 📌 Dosya Yükleme Bileşeni
uploaded_file = st.file_uploader(
    "Bir ses veya video dosyası yükleyin (MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC)",
    type=["mp3", "wav", "mp4", "m4a", "ogg", "caf", "aac", "flac"]
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    
    # 📥 Geçici dosyaya kaydet
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
    temp_audio_file.write(uploaded_file.read())
    temp_audio_file.close()
    
    # 🎯 WAV formatına çevir
    wav_filename = convert_to_wav(temp_audio_file.name)
    os.remove(temp_audio_file.name)
    
    if wav_filename:
        st.write("🔄 Ses dosyanız işleniyor, lütfen bekleyin...")

        # 🔄 Large model yerine medium model kullan (VRAM Optimizasyonu)
        whisper_model = whisper.load_model("tmedium")

        result = transcribe_audio(wav_filename, whisper_model)
        os.remove(wav_filename)
        
        if "text" in result:
            transcribed_text = result["text"]
            segments = result["segments"]
            
            st.subheader("📝 Transkripsiyon Sonucu")
            st.text_area("Çıktı:", transcribed_text, height=250)
            
            json_output = json.dumps(segments, ensure_ascii=False, indent=4)
            st.download_button("📥 JSON Formatında İndir", json_output, file_name="transcription.json", mime="application/json")
            
            # 📝 SRT Formatına Çevirme
            srt_writer = get_writer("srt", ".")
            srt_filename = tempfile.NamedTemporaryFile(delete=False, suffix=".srt").name
            srt_writer(result, srt_filename)
            
            with open(srt_filename, "r", encoding="utf-8") as file:
                srt_content = file.read()
            os.remove(srt_filename)
            
            st.download_button("📥 Düz Metni İndir", transcribed_text, file_name="transcription.txt", mime="text/plain")
            st.download_button("📥 Zaman Damgalı Altyazı (SRT) İndir", srt_content, file_name="transcription.srt", mime="text/plain")

clear_temp_files()  # Geçici dosyaları temizle


