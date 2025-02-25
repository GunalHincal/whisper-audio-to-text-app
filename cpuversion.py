import streamlit as st
import whisper
import tempfile
import os
import json
import time
import torch
import io
import ffmpeg
import psutil  # 🔥 CPU Kullanımını Gösteren Kütüphane

# ✅ **Streamlit yapılandırmasını en başta ayarla!**
st.set_page_config(page_title="Whisper Ses Transkripsiyon", layout="centered")

# 📊 **CPU Kullanımı Fonksiyonu**
def get_cpu_usage():
    """Sistemin CPU ve RAM kullanımını döndürür."""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    return cpu_percent, ram_percent

# 🎯 **CPU Kullanımını Sidebar'da Göster**
st.sidebar.header("🖥️ CPU Kullanımı")
cpu_percent, ram_percent = get_cpu_usage()
st.sidebar.write(f"⚙️ İşlemci Kullanımı: {cpu_percent:.2f}%")
st.sidebar.write(f"💾 RAM Kullanımı: {ram_percent:.2f}%")

# 📌 **İşlem Durumu için Progress Bar**
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.title("🎙️ Ses veya Video Dosyası Yükleyin ve Metne Çevirin")

# 📌 **Ses Dönüştürme Fonksiyonu (FFmpeg ile)**
def convert_to_wav(input_path):
    """ Ses veya video dosyasını WAV formatına çevirir (FFmpeg kullanarak). """
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

# 📌 **Transkripsiyon Fonksiyonu (İlerleme Çubuğu ile)**
def transcribe_audio(audio_path, model):
    """ Whisper modeli ile transkripsiyon yapar ve ilerleme çubuğunu günceller. """
    result = model.transcribe(audio_path, fp16=False)
    
    # 🔹 Segment sayısına göre ilerleme çubuğunu güncelle
    num_segments = len(result["segments"])
    
    for i, _ in enumerate(result["segments"]):
        progress = int(((i + 1) / num_segments) * 100)  # İlerleme yüzdesini hesapla
        progress_bar.progress(progress)
        time.sleep(0.1)  # Küçük bir gecikme ekleyerek güncellemeleri görmeyi sağla
    
    return result

# 📌 **SRT Dosyası Üreten Fonksiyon**
def generate_srt(segments):
    """ Segmentlerden SRT dosyası oluşturur. """
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
        status_text.text("🔄 Transkripsiyon devam ediyor...")

        # 🔄 **Medium model kullan (CPU'ya alındı)**
        whisper_model = whisper.load_model("medium").to("cpu")  # 🔥 CPU'ya geçirildi

        result = transcribe_audio(wav_filename, whisper_model)
        os.remove(wav_filename)

        # 🎯 **İşlem tamamlandı, ilerleme çubuğunu %100 yap**
        progress_bar.progress(100)
        status_text.text("✅ Transkripsiyon tamamlandı!")

        if "text" in result:
            transcribed_text = result["text"]
            segments = result["segments"]

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
