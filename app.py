import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64

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

    st.write("• Tamil")
    st.write("• Hindi")
    st.write("• Spanish")
    st.write("• French")


# Description
st.write("Real-time Multilingual Communication Assistant")

st.markdown("---")


# User Input
user_text = st.text_input(
    "Enter your text:"
)

# Languages
languages = {
    "Tamil": "ta",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr"
}

selected_language = st.selectbox(
    "Choose Target Language:",
    list(languages.keys())
)


# Translate Button
if st.button("Translate"):

    if user_text.strip() == "":
        st.warning("Please enter some text.")

    else:

        with st.spinner("Translating..."):

            translated = GoogleTranslator(
                source="auto",
                target=languages[selected_language]
            ).translate(user_text)

        st.session_state.translated = translated

        st.session_state.selected_lang_code = (
            languages[selected_language]
        )

        st.session_state.history.append({

            "original": user_text,
            "translated": translated,
            "language": selected_language
        })


# Translation Display
if st.session_state.translated:

    # Generate audio
    tts = gTTS(
        text=st.session_state.translated,
        lang=st.session_state.selected_lang_code
    )

    tts.save("translation.mp3")

    with open(
        "translation.mp3",
        "rb"
    ) as f:

        audio_bytes = f.read()

    audio_base64 = base64.b64encode(
        audio_bytes
    ).decode()

    col1, col2, col3 = st.columns([8,1.5,1.5])

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


# Translation History
if st.session_state.history:

    st.markdown("---")

    st.subheader(
        "Translation History"
    )

    for item in reversed(
        st.session_state.history
    ):

        st.write(
            f"Original: {item['original']}"
        )

        st.write(
            f"Translated ({item['language']}): "
            f"{item['translated']}"
        )

        st.markdown("---")


# Clear History
if st.button(
    "Clear History"
):

    st.session_state.history = []

    st.session_state.translated = ""

    st.rerun()


# Footer
st.markdown("---")

st.caption(
    "Built with Python + Streamlit"
)
