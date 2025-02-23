# streamlit-whisper-app


## **Whisper Speech-to-Text API with Streamlit**

This project provides a **speech-to-text** transcription tool using **OpenAI's Whisper model**. Users can upload audio files via a **Streamlit web application**, select from multiple Whisper model sizes, and receive transcriptions in **text, JSON, and SRT formats**.

https://github.com/openai/whisper
----------

## **🚀 Features**

✅ **Multiple Model Selection:** Supports different Whisper model sizes (**tiny, base, small, medium, large, turbo**) for speed vs. accuracy trade-offs.  

✅ **Real-Time Model Information:** Displays **VRAM requirements, speed, and accuracy** for each selected model.  

✅ **Supports Various Audio Formats:** Accepts **MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC** file formats.  

✅ **Dynamic Transcription Options:** Returns **raw text, JSON with timestamps, and SRT subtitles**.  

✅ **Automatic Audio Conversion:** Converts non-WAV files to WAV for optimal processing using **FFmpeg**.  

✅ **Streamlit UI for Easy Interaction:** No coding required—just **upload an audio file and get transcriptions instantly!**

----------

## **📌 Whisper Model Options**


**Görsel**

----------

## **🛠️ Requirements**

-   **Python 3.8+**
-   **FFmpeg** (for audio conversion)
-   **Streamlit** (for UI)
-   **Whisper from OpenAI** (for transcription)
-   **Python dependencies** (stored in `requirements.txt`)

----------

## **⚙️ Installation**

### **1️⃣ Clone the Repository**

bash

`git clone https://github.com/GunalHincal/whisper-stt-app.git
cd whisper-stt-app` 

### **2️⃣ Install Dependencies**

bash

`pip install -r requirements.txt` 

### **3️⃣ Run the Application**

bash

`streamlit run app.py` 

----------

## **🖥️ Using the Application**

### **1️⃣ Select a Whisper Model**

-   Choose from **tiny, base, small, medium, large, or turbo** based on your system’s **VRAM** and required **accuracy**.

### **2️⃣ Upload an Audio File**

-   Supported formats: **MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC**.

### **3️⃣ Get Transcription in Multiple Formats**

-   **Plain Text**: Direct text transcription.
-   **JSON**: Includes **timestamps** for each segment.
-   **SRT**: Subtitle format for videos.

### **4️⃣ Download Transcriptions**

-   Save results as **.txt, .json, or .srt** for later use.

ow, you can access the app at:

arduino

`http://localhost:8501` 

----------

## **⚠️ Known Issues**

🔴 **High VRAM Usage:** **Large and turbo models require significant VRAM (~6-10GB).** Choose a smaller model if you face performance issues.  

🔴 **Unsupported Audio Formats:** Ensure uploaded files are in **MP3, WAV, MP4, M4A, OGG, CAF, AAC, or FLAC** formats.  

🔴 **Slow Transcription on Large Models:** Use **tiny, base, or small** for faster results.

----------

## **🤝 Contribution**

Want to improve this project? Follow these steps:

1.  **Fork this repository**.
2.  **Create a new branch**:
    
    bash

    `git checkout -b feature/your-feature` 
    
3.  **Make changes and commit**:
    
    bash
    
    `git commit -m "Added a new feature"` 
    
4.  **Push your branch**:
    
    bash
 
    `git push origin feature/your-feature` 
    
5.  **Open a Pull Request**.

----------

## **📢 Follow Me for More Updates**

Stay connected and follow me for updates on my projects, insights, and tutorials:

🔗 **LinkedIn**: [Connect with me professionally to learn more about my work and collaborations.](https://www.linkedin.com/in/gunalhincal/)  

📖 **Medium**: [Check out my blog for articles on technology, data science, and more!](https://medium.com/@hincalgunal)

🚀 **Feel free to reach out!** 



----------

# **Whisper Speech-to-Text API with Streamlit**

Bu proje, **OpenAI Whisper modeli** kullanarak ses dosyalarını metne çeviren bir **Streamlit tabanlı web uygulaması** sunar. Kullanıcılar **farklı Whisper model boyutlarını seçerek**, hız ve doğruluk arasında seçim yapabilirler.

----------

## **🚀 Özellikler**

✅ **Farklı Whisper Modelleri:** **tiny, base, small, medium, large, turbo** seçenekleriyle **hız ve doğruluk** ayarlanabilir.  

✅ **Kullanıcı Dostu Arayüz:** **Streamlit UI** üzerinden kolayca **ses dosyası yüklenir, model seçilir ve metne çevirme işlemi yapılır**.  

✅ **Geniş Ses Format Desteği:** **MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC** gibi yaygın formatları destekler.  

✅ **Otomatik Ses Dönüştürme:** **MP3 gibi formatları otomatik olarak WAV’a çevirir**.  

✅ **Çoklu Çıktı Formatları:** **TXT, JSON (timestamp'li), SRT (altyazı)** olarak transkript edilebilir.
  
✅ **Hızlı Model Önbellekleme:** **Model bir kez yüklenir ve tüm sorgular için bellekte saklanır**, böylece her işlemde **yeniden yüklenmez**.

----------

## **📌 Desteklenen Whisper Modelleri**

**Görsel**


----------

## **📥 Kurulum**

### **1️⃣ Depoyu Kopyalayın**

bash

`git clone https://github.com/GunalHincal/whisper-stt-app.git
cd whisper-stt-app` 

### **2️⃣ Gerekli Bağımlılıkları Yükleyin**

bash

`pip install -r requirements.txt` 

### **3️⃣ Uygulamayı Başlatın**

bash

`streamlit run app.py` 

Arayüz **http://localhost:8501** adresinde çalışacaktır.

----------

## **🖥️ Uygulama Kullanımı**

### **1️⃣ Model Seçimi**

-   **tiny, base, small, medium, large, turbo** modellerinden birini seçin.
-   **VRAM durumunuza ve doğruluk ihtiyacınıza göre** uygun modeli seçebilirsiniz.

### **2️⃣ Ses Dosyası Yükleme**

-   Desteklenen formatlar: **MP3, WAV, MP4, M4A, OGG, CAF, AAC, FLAC**
-   Ses dosyanız **WAV formatına otomatik dönüştürülür**.

### **3️⃣ Transkripsiyon İşlemi**

-   **Metin Çıkışı:** Düz metin halinde transkripsiyon.
-   **JSON Çıkışı:** Zaman damgalı segmentler ile transkripsiyon.
-   **SRT Çıkışı:** **Altyazı formatında** çıktı oluşturulabilir.

### **4️⃣ Çıktıyı İndirme**

-   **TXT, JSON, SRT** formatlarında transkripsiyon sonuçlarını indirebilirsiniz.

----------

## **⚠️ Bilinen Sorunlar**

🔴 **Büyük Modellerde Performans Sorunu:** **Large ve Turbo modelleri yüksek VRAM gerektirir (~6-10GB).** Donanımınız yetersizse **tiny veya base** modellerini kullanabilirsiniz.  

🔴 **Yüksek İşlem Süresi:** **Daha büyük modeller (large, turbo) daha yavaş çalışır.** Daha hızlı sonuçlar için **tiny veya base kullanın**.

----------

## **🤝 Katkıda Bulunma**

1.  **Depoyu Fork'layın.**
2.  **Yeni bir branch oluşturun:**
    
    bash
    
    `git checkout -b feature/your-feature` 
    
3.  **Değişikliklerinizi commit edin:**
    
    bash
    
    `git commit -m "Yeni özellik eklendi"` 
    
4.  **Branch'i push edin:**
  
    bash
    
    `git push origin feature/your-feature` 
    
5.  **Pull Request açın.**

----------

## **📢 Bağlantılar & İletişim**

🔗 **LinkedIn**: [LinkedIn Profilim](https://www.linkedin.com/in/gunalhincal/)  
📖 **Medium**: [Blog Yazılarım](https://medium.com/@hincalgunal)

📌 **Sorularınız için bana ulaşabilirsiniz!** 🚀
