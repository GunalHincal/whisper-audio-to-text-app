import streamlit as st
import whisper
import tempfile
import os
import json
import ffmpeg
import time
import torch
import io
from pydub import AudioSegment  # ✅ Pydub kullanarak FFmpeg ihtiyacını çözüyoruz
import subprocess

# 🏗️ Sayfa Yapılandırması
st.set_page_config(page_title="Whisper Ses Transkripsiyon", layout="centered")

st.title("🎙️ Ses veya Video Dosyası Yükleyin ve Metne Çevirin")

# 🔄 **FFmpeg'in sistemde olup olmadığını kontrol et**
def is_ffmpeg_available():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

# 🔄 FFmpeg kullanılabilir değilse hata ver
if not is_ffmpeg_available():
    st.error("⚠️ FFmpeg bulunamadı! Lütfen sisteminize FFmpeg yükleyin veya 'ffmpeg-python' kütüphanesini kullanın.")

# 🛠 **CUDA Kullanılabilirlik Kontrolü**
device = "cuda" if torch.cuda.is_available() else "cpu"

# 📊 GPU Kullanımı Fonksiyonu
def get_gpu_usage():
    if device == "cuda":
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        return allocated, reserved
    return 0, 0

# 🎯 GPU Kullanımını Sidebar'da Göster
st.sidebar.header("📊 GPU Kullanımı")
allocated, reserved = get_gpu_usage()
st.sidebar.write(f"💾 Ayrılmış Bellek: {allocated:.2f} GB")
st.sidebar.write(f"🔒 Rezerve Edilen Bellek: {reserved:.2f} GB")

# 📌 **Ses Dönüştürme Fonksiyonu**
def convert_to_wav(input_path):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1)  # 🔄 Whisper için uygun hale getir
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        st.error(f"⚠️ Ses dönüştürme hatası: {e}")
        return None

# 📌 **Transkripsiyon Fonksiyonu**
def transcribe_audio(audio_path, model):
    result = model.transcribe(audio_path, fp16=False)
    return result

# 📌 **SRT Dosyası Üreten Fonksiyon**
def generate_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]

        # 🕒 Zaman formatını (SRT formatına) çevir
        start_srt = time.strftime("%H:%M:%S", time.gmtime(start_time)) + f",{int((start_time % 1) * 1000):03d}"
        end_srt = time.strftime("%H:%M:%S", time.gmtime(end_time)) + f",{int((end_time % 1) * 1000):03d}"

        srt_content += f"{i+1}\n{start_srt} --> {end_srt}\n{text}\n\n"

    return srt_content

# 📌 **Dosya Yükleme Bileşeni**
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

        # 🔄 **Medium model kullan ve GPU varsa ona yükle**
        whisper_model = whisper.load_model("medium").to(device)

        result = transcribe_audio(wav_filename, whisper_model)
        os.remove(wav_filename)

        if "text" in result:
            transcribed_text = result["text"]
            segments = result["segments"]

            # **🔥 Debug: Segmentlerin içeriğini terminale yaz**
            print("✅ Segmentlerin İçeriği:")
            print(json.dumps(segments, indent=4, ensure_ascii=False))

            st.subheader("📝 Transkripsiyon Sonucu")
            st.text_area("Çıktı:", transcribed_text, height=250)

            json_output = json.dumps(segments, ensure_ascii=False, indent=4)

            # **📝 SRT Dosyasını Manuel Oluştur**
            srt_content = generate_srt(segments)

            # 🔍 **Debug için içeriği terminale yazdıralım**
            print("✅ SRT Dosyası İçeriği:")
            print(srt_content)

            # **Eğer dosya boşsa hata mesajı göster**
            if not srt_content.strip():
                st.error("❌ Hata: Oluşturulan SRT dosyası boş!")
                print("❌ DEBUG: SRT dosyası boş oluşturuldu, segmentler kontrol edilmeli.")
            else:
                # ✅ **Streamlit butonları ekleyelim**
                st.download_button("📥 JSON Formatında İndir", json_output, file_name="transcription.json", mime="application/json")
                st.download_button("📥 Düz Metni İndir", transcribed_text, file_name="transcription.txt", mime="text/plain")
                
                # 🔄 **BytesIO ile SRT Dosyasını Doğru Şekilde Ver**
                srt_buffer = io.BytesIO(srt_content.encode("utf-8"))
                st.download_button("📥 Zaman Damgalı Altyazı (SRT) İndir", srt_buffer, file_name="transcription.srt", mime="text/plain")
