import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import langid
import base64
import pyperclip
from streamlit_mic_recorder import mic_recorder
from datetime import datetime


# Page Configuration
st.set_page_config(
    page_title="LinguaLive",
    page_icon="🌍",
    layout="centered"
)


# Session State
if "history" not in st.session_state:
    st.session_state.history = []

if "translated" not in st.session_state:
    st.session_state.translated = ""

if "selected_lang_code" not in st.session_state:
    st.session_state.selected_lang_code = ""

if "detected_language" not in st.session_state:
    st.session_state.detected_language = ""


# Title
st.title("🌍 LinguaLive")


# Sidebar
with st.sidebar:

    st.header("About")

    st.write(
        "LinguaLive is a multilingual communication assistant "
        "built using Python and Streamlit."
    )

    st.markdown("---")

    st.subheader("Supported Languages")

    supported_languages = [

        "Tamil",
        "Hindi",
        "Spanish",
        "French",
        "English",
        "German",
        "Italian",
        "Japanese",
        "Korean",
        "Arabic",
        "Portuguese",
        "Russian"

    ]

    for lang in supported_languages:

        st.write(
            f"• {lang}"
        )


# Description
st.write(
    "Real-time Multilingual Communication Assistant"
)

st.markdown("---")


# User Input
user_text = st.text_input(
    "Enter your text:"
)


# Voice Input
st.markdown(
    "### 🎤 Voice Input"
)

voice_data = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    key="recorder"
)

if voice_data:

    st.success(
        "Voice recorded successfully 🎤"
    )

    st.info(
        "Speech-to-text processing coming next"
    )


# Languages
languages = {

    "Tamil": "ta",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "English": "en",
    "German": "de",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru"

}


selected_language = st.selectbox(
    "Choose Target Language:",
    list(languages.keys())
)


# Translate Button
if st.button(
    "Translate"
):

    if user_text.strip() == "":

        st.warning(
            "Please enter some text."
        )

    else:

        with st.spinner(
            "Translating..."
        ):

            try:

                translated = GoogleTranslator(
                    source="auto",
                    target=languages[selected_language]
                ).translate(
                    user_text
                )

            except Exception:

                st.error(
                    "Translation service unavailable. Please try again."
                )

                st.stop()

        # Language Detection
        try:

            detected_language_code, _ = (
                langid.classify(
                    user_text
                )
            )

            language_names = {

                "en": "English",
                "ta": "Tamil",
                "hi": "Hindi",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "ja": "Japanese",
                "ko": "Korean",
                "ar": "Arabic"

            }

            st.session_state.detected_language = (
                language_names.get(
                    detected_language_code,
                    detected_language_code.upper()
                )
            )

        except:

            st.session_state.detected_language = (
                "Unknown"
            )


        st.session_state.translated = translated

        st.session_state.selected_lang_code = (
            languages[selected_language]
        )


        # History storage
        st.session_state.history.append({

            "original": user_text,
            "translated": translated,
            "language": selected_language,
            "time": datetime.now().strftime(
                "%H:%M:%S"
            )

        })


# Translation Output
if st.session_state.translated:

    st.markdown(
        f"🌐 **Detected Language:** "
        f"{st.session_state.detected_language}"
    )


    # Audio generation
    tts = gTTS(
        text=st.session_state.translated,
        lang=st.session_state.selected_lang_code
    )

    tts.save(
        "translation.mp3"
    )


    with open(
        "translation.mp3",
        "rb"
    ) as f:

        audio_bytes = f.read()


    audio_base64 = base64.b64encode(
        audio_bytes
    ).decode()


    col1, col2, col3, col4 = st.columns(
        [8,1.5,1.5,1.5]
    )


    with col1:

        st.success(
            st.session_state.translated
        )


    with col2:

        if st.button(
            "🔊",
            use_container_width=True
        ):

            st.markdown(
                f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                """,
                unsafe_allow_html=True
            )


    with col3:

        st.download_button(
            "📥",
            audio_bytes,
            file_name="translation.mp3",
            mime="audio/mp3",
            use_container_width=True
        )


    with col4:

        if st.button(
            "📋",
            use_container_width=True
        ):

            pyperclip.copy(
                st.session_state.translated
            )

            st.toast(
                "Copied ✅"
            )


# Translation History
if st.session_state.history:

    st.markdown("---")

    st.subheader(
        "📜 Translation History"
    )

    for index, item in enumerate(
        reversed(st.session_state.history)
    ):

        col1, col2 = st.columns(
            [10,1]
        )

        with col1:

            st.info(
                f"""
Original: {item['original']}

Language: {item['language']}

Translation: {item['translated']}

Time: {item['time']}
                """
            )

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{index}"
            ):

                actual_index = (
                    len(st.session_state.history)
                    -1
                    -index
                )

                st.session_state.history.pop(
                    actual_index
                )

                st.rerun()


# Clear History
if st.button(
    "Clear History"
):

    st.session_state.history = []
    st.session_state.translated = ""
    st.session_state.detected_language = ""

    st.rerun()


# Footer
st.markdown("---")

st.caption(
    "Built with Python + Streamlit"
)