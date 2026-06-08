import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import langid
import pyperclip
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# Speech → Text preparation
import speech_recognition as sr
from pydub import AudioSegment
import io
import os

FFMPEG_PATH = r"C:\Users\navee\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

AudioSegment.converter = os.path.join(
    FFMPEG_PATH,
    "ffmpeg.exe"
)

AudioSegment.ffmpeg = os.path.join(
    FFMPEG_PATH,
    "ffmpeg.exe"
)

AudioSegment.ffprobe = os.path.join(
    FFMPEG_PATH,
    "ffprobe.exe"
)

os.environ["PATH"] += os.pathsep + FFMPEG_PATH


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="LinguaLive",
    page_icon="🌍",
    layout="centered"
)

# ---------------- SESSION STATE ----------------

if "history" not in st.session_state:
    st.session_state.history=[]

if "translated" not in st.session_state:
    st.session_state.translated=""

if "selected_lang_code" not in st.session_state:
    st.session_state.selected_lang_code=""

if "detected_language" not in st.session_state:
    st.session_state.detected_language=""

if "selected_language" not in st.session_state:
    st.session_state.selected_language="Tamil"

if "voice_audio_bytes" not in st.session_state:
    st.session_state.voice_audio_bytes=None

if "detected_speech_text" not in st.session_state:
    st.session_state.detected_speech_text=""

if "text_input_value" not in st.session_state:
    st.session_state.text_input_value=""

if "reuse_text" not in st.session_state:
    st.session_state.reuse_text=""


default_text=""


if "reuse_text" in st.session_state:

    default_text=st.session_state["reuse_text"]

    del st.session_state["reuse_text"]

# ---------------- LANGUAGES ----------------

languages={

    "Tamil":"ta",
    "Hindi":"hi",
    "Spanish":"es",
    "French":"fr",
    "English":"en",
    "German":"de",
    "Italian":"it",
    "Japanese":"ja",
    "Korean":"ko",
    "Arabic":"ar",
    "Portuguese":"pt",
    "Russian":"ru"

}

language_names={

    "en":"English",
    "ta":"Tamil",
    "hi":"Hindi",
    "es":"Spanish",
    "fr":"French",
    "de":"German",
    "it":"Italian",
    "pt":"Portuguese",
    "ru":"Russian",
    "ja":"Japanese",
    "ko":"Korean",
    "ar":"Arabic"

}

# ---------------- SPEECH TO TEXT ----------------

def use_detected_speech():

    st.session_state.text_input_value=(
        st.session_state.detected_speech_text
    )


def speech_to_text(audio_bytes):

    recognizer=sr.Recognizer()

    try:

        audio=AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="webm"
        )

        audio=audio.set_channels(
            1
        ).set_frame_rate(
            16000
        )

        wav_io=io.BytesIO()

        audio.export(
            wav_io,
            format="wav"
        )

        wav_io.seek(0)

        with sr.AudioFile(
            wav_io
        ) as source:

            audio_data=recognizer.record(
                source
            )

        text=recognizer.recognize_google(
            audio_data
        )

        return text


    except sr.UnknownValueError:

        return None


    except sr.RequestError:

        return None


    except Exception as e:

        st.error(
            f"Speech processing error: {e}"
        )

        return None

# ---------------- TITLE ----------------

st.title("🌍 LinguaLive")

st.write(
    "Real-time Multilingual Communication Assistant"
)

st.markdown("---")

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("🌍 About LinguaLive")

    st.markdown("""
LinguaLive is an **AI-powered multilingual communication platform**
designed to reduce language barriers in real-time conversations.
""")

    st.markdown("---")

    st.subheader("⚡ Current Capabilities")

    st.markdown("""
✅ Text → Text Translation  

✅ Text → Speech  

✅ Speech → Text *(in progress)*  

✅ Speech → Speech *(in progress)*  

✅ Translation History  

✅ Automatic Language Detection  

✅ Audio Generation & Playback
""")

    st.markdown("---")

    st.subheader("🚀 Future Vision")

    st.markdown("""
Enable people speaking different languages to communicate naturally.

Each person speaks in their own language while hearing the conversation in their preferred language.
""")

    st.markdown("---")

    st.subheader("🎯 Focus")

    st.info(
        "Fast • Natural • Real-time Communication"
    )

    st.markdown("---")

    st.subheader(
        f"🌐 Languages Supported ({len(languages)})"
    )

    with st.expander("View Languages"):

        for lang in languages.keys():

            st.write(f"• {lang}")

# ---------------- MODE SELECTOR ----------------

mode=st.radio(

    "Choose Mode",

    [

        "Translation Assistant",
        "Live Communication"

    ]

)

st.markdown("---")

# ======================================================
# LIVE COMMUNICATION MODE
# ======================================================

if mode=="Live Communication":

    st.subheader(
        "📞 Call Setup"
    )

    my_language=st.selectbox(

        "I Speak:",

        list(
            languages.keys()
        ),

        key="my_language"

    )

    hear_language=st.selectbox(

        "I Want To Hear:",

        list(
            languages.keys()
        ),

        key="hear_language"

    )

    st.success(

f"""
Your Language: {my_language}

Hear Language: {hear_language}
"""

    )

    if st.button(

        "🟢 Start Session",
        use_container_width=True

    ):

        st.success(
            "Session Ready ✅"
        )

        st.markdown(

f"""
🎤 Listening...

Speaking Language: {my_language}

Hearing Language: {hear_language}
"""

        )

        st.info(
            "Live translation engine coming next 🚀"
        )

# ======================================================
# TRANSLATION ASSISTANT MODE
# ======================================================

else:

    if "reuse_text" in st.session_state and st.session_state.reuse_text!="":

        st.session_state.text_input_value=(
            st.session_state.reuse_text
        )

        st.session_state.reuse_text=""


    user_text=st.text_input(
        "Enter your text:",
        key="text_input_value"
    )

    st.markdown(
        "### 🎤 Voice Input"
    )

    voice_data=mic_recorder(

        start_prompt="Start Recording",

        stop_prompt="Stop Recording",

        key="recorder"

    )

    if voice_data and "bytes" in voice_data:

        st.session_state.voice_audio_bytes=voice_data[
            "bytes"
        ]

        st.success(
            "Voice recorded successfully 🎤"
        )
        
        if st.session_state.voice_audio_bytes:

         if st.button(
            "🎙 Convert Speech to Text"
        ):

            speech_text=speech_to_text(
                st.session_state.voice_audio_bytes
            )

            if speech_text:

                st.session_state.detected_speech_text=speech_text
                

            else:

                st.warning(
                    "Could not recognize speech"
                )


    if st.session_state.detected_speech_text:

        st.success(
            f"Detected Speech: {st.session_state.detected_speech_text}"
        )

        st.button(
    "Use Detected Speech",
    on_click=use_detected_speech
)


    col1,col2=st.columns([8,2])

            

    with col1:

        selected_language=st.selectbox(

            "Choose Target Language:",

            list(
                languages.keys()
            ),

            index=list(
                languages.keys()
            ).index(
                st.session_state.selected_language
            )

        )

    with col2:

        st.write("")
        st.write("")

        swap=st.button(
            "🔄",
            help="Swap"
        )

    st.session_state.selected_language=selected_language

    if swap:

        reverse_languages={

            value:key
            for key,value
            in languages.items()

        }

        detected=(
            st.session_state.detected_language
        )

        code=None

        for k,v in language_names.items():

            if v==detected:

                code=k

        if code and code in reverse_languages:

            st.session_state.selected_language=(

                reverse_languages[
                    code
                ]

            )

            st.rerun()

        else:

            st.warning(
                "Translate once before swapping"
            )


    if st.button(
        "Translate"
    ):

        if user_text.strip()=="":

            st.warning(
                "Please enter text"
            )

        else:

            translated=GoogleTranslator(

                source="auto",

                target=languages[
                    selected_language
                ]

            ).translate(
                user_text
            )

            detected_code,_=(

                langid.classify(
                    user_text
                )

            )

            st.session_state.detected_language=(

                language_names.get(
                    detected_code,
                    "Unknown"
                )

            )

            st.session_state.translated=translated

            st.session_state.selected_lang_code=(

                languages[
                    selected_language
                ]

            )

            st.session_state.history.append({

                "original":user_text,
                "translated":translated,
                "language":selected_language,
                "time":datetime.now().strftime(
                    "%H:%M:%S"
                )

            })


    if st.session_state.translated:

        st.markdown(

f"🌐 Detected Language: {st.session_state.detected_language}"

        )

        tts=gTTS(

            text=st.session_state.translated,

            lang=st.session_state.selected_lang_code

        )

        tts.save(
            "translation.mp3"
        )

        with open(

            "translation.mp3",

            "rb"

        ) as file:

            audio_bytes=file.read()

        col1,col2,col3=st.columns(
            [8,1,1]
        )

        with col1:

            st.success(
                st.session_state.translated
            )

        with col2:

            st.audio(

                audio_bytes,

                format="audio/mp3"

            )

        with col3:

            if st.button(

                "📋",

                key="copy_translation",
                help="Copy"

            ):

                pyperclip.copy(
                    st.session_state.translated
                )

                st.toast(
                    "Copied ✅"
                )


    # ---------------- TRANSLATION HISTORY ----------------

    if st.session_state.history:

        st.markdown("---")

        col1,col2=st.columns([8,2])

        with col1:

            st.subheader(
                "🕒 Translation History"
            )

        with col2:

            st.write("")

            if st.button(

                "🗑️ Clear All",

                key="clear_history"
    

            ):

                st.session_state.history=[]

                st.toast(
                    "History cleared ✅"
                )

                st.rerun()

        for i,item in enumerate(

            reversed(
                st.session_state.history
            )

        ):

            col1,col2,col3=st.columns([8,1,1])

            with col1:

                st.success(

f"""
Original: {item['original']}

Translated ({item['language']}): {item['translated']}

🕒 {item['time']}
"""

                )

            with col2:

                if st.button(

                    "🗑️",

                    key=f"delete_{i}",
                    help="Clear"

                ):

                    original_index=(

                        len(
                            st.session_state.history
                        )-1-i

                    )

                    del st.session_state.history[
                        original_index
                    ]

                    st.rerun()

            with col3:

                if st.button(

                    "↩️",

                    key=f"reuse_{i}",
                    help="Reuse"

                ):

                    st.session_state[
                        "reuse_text"
                    ]=item[
                        "original"
                    ]

                    st.rerun()

# ---------------- FOOTER ----------------

st.markdown("---")

st.caption(
    "Built with Python + Streamlit"
)