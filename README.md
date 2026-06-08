
# 🌍 LinguaLive

LinguaLive is an AI-powered, real-time multilingual communication platform built using **Python** and **Streamlit**. 

The core mission of LinguaLive is to enable natural, fluid conversations between people speaking different languages—completely eliminating the need for manual translation. Rather than functioning as a simple text translator, LinguaLive is evolving into a live multilingual communication assistant capable of seamless, end-to-end speech handling.

### Core Capabilities
* **🎙️ Speech Recognition:** High-accuracy voice-to-text processing.
* **🌐 Language Detection:** Automatic identification of spoken or written languages.
* **⚡ Real-Time Translation:** Low-latency translation across multiple language pairs.
* **🔊 Speech Synthesis:** Natural-sounding text-to-speech generation.
* **🗣️ Multilingual Voice Communication:** Twin-way continuous voice interpretation.

---

## 🚀 Vision & Final Product Goal

LinguaLive aims to bridge language gaps entirely, making cross-lingual communication feel as natural as a face-to-face conversation.


```
[Person A (Tamil)] ──> (Transcription) ──> (Translation to English) ──> (Speech Generation) ──> [Person B (English)]
│
▼
[Person A (Tamil)] <── (Speech Generation) <── (Translation to Tamil) <── (Transcription) <── [Person B (English)]
```

The long-term vision is to establish a robust, real-time multilingual voice communication ecosystem, operating much like a dedicated, live AI interpreter.

---

## ⚡ Features & Development Progress

### 🧩 Current Features (Translation Assistant)
* **Text ──> Text Translation:** Instant text translation across supported languages.
* **Text ──> Speech:** Synthetic voice generation from translated text.
* **Speech ──> Text:** Accurate transcription of voice inputs.
* **Speech ──> Fill Input Workflow:** Seamless UX workflow to dictate text into inputs.
* **Automatic Language Detection:** Auto-detects source language without manual toggling.
* **Translation History & Reuse:** Local tracking of previous translations for quick access.
* **Audio Playback & Copy:** Simple UI controls to replay generated audio or copy text.
* **Session State Management:** Reliable Streamlit session handling to preserve app state.

### 📡 Live Communication (In Progress)
* [x] Call Setup Architecture
* [x] Language Preference Selection
* [ ] **🚧 Real-Time Communication Engine**
* [ ] **🚧 Continuous Speech Translation**
* [ ] **🚧 Streaming Audio Pipeline**

---

## 🧠 System Architecture & Pipelines

The project is being developed incrementally with a strict focus on architectural stability, clean state management, modular workflows, and real-time communication foundations.

### Application Workflow

```
[Voice Input] ──> [Speech Recognition] ──> [Language Detection] ──> [Translation] ──> [Speech Generation]
```

### 🔊 Speech Pipeline Details

```
[Microphone Input]
│
▼
[WebM Audio Capture]
│
▼
[FFmpeg Conversion]
│
▼
[WAV Processing]
│
▼
[Speech Recognition]
│
▼
[Text Output]
```

---

## 🛠️ Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **🎨 Frontend** | Streamlit |
| **⚙️ Backend & AI** | Python, deep-translator, SpeechRecognition, gTTS, langid, pydub, FFmpeg |

---

## 🌐 Supported Languages

LinguaLive currently supports the following languages, with more being integrated gradually:

* 🇺🇸 English
* 🇮🇳 Tamil
* 🇮🇳 Hindi
* 🇪🇸 Spanish
* 🇫🇷 French
* 🇩🇪 German
* 🇮🇹 Italian
* 🇯🇵 Japanese
* 🇰🇷 Korean
* 🇸🇦 Arabic
* 🇵🇹 Portuguese
* 🇷🇺 Russian

---

## 📌 Current Phase & Future Roadmap

LinguaLive is currently transitioning from a standalone **Translation Tool** into a **Speech Translator**, on its way to becoming a fully realized **Real-Time Voice Communication Platform**.

### 🎯 Current Focus Areas
* Stabilizing underlying speech workflows.
* Improving user experience (UX) and reducing interaction friction.
* Finalizing foundations for the real-time communication architecture.

### 🔮 Planned Features
* **Real-time speech-to-speech translation**
* **Live multilingual conversation sessions**
* **WebRTC-based communication** for direct peer connectivity
* **Streaming translation pipelines** to process audio chunks mid-speech
* **Speaker-aware conversations** (multi-speaker diarization)
* **Faster, local speech recognition models** (e.g., Whisper optimizations)
* **AI-enhanced translation quality** for localized idioms and context
* **Low-latency voice delivery** systems

---

## 👨‍💻 Project Status

> **🚧 Active Development**
> 
> This project is being engineered incrementally using robust product practices, scalable communication principles, and highly modular AI workflows.

```
