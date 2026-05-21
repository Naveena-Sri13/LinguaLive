import streamlit as st
from deep_translator import GoogleTranslator

# Page Configuration
st.set_page_config(
    page_title="LinguaLive",
    page_icon="🌍",
    layout="centered"
)

# Store translation history
if "history" not in st.session_state:
    st.session_state.history = []

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

# Divider
st.markdown("---")

# User Input
user_text = st.text_input("Enter your text:")

# Language Options
languages = {
    "Tamil": "ta",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr"
}

# Dropdown
selected_language = st.selectbox(
    "Choose Target Language:",
    list(languages.keys())
)

# Translate Button
if st.button("Translate"):

    # Empty Input Check
    if user_text.strip() == "":
        st.warning("Please enter some text.")

    else:

        # Loading animation
        with st.spinner("Translating..."):

            translated = GoogleTranslator(
                source='auto',
                target=languages[selected_language]
            ).translate(user_text)

        # Output
        st.subheader("Translated Text")
        st.success(translated)

        # Save History
        st.session_state.history.append({
            "original": user_text,
            "translated": translated,
            "language": selected_language
        })

# Translation History
if st.session_state.history:

    st.markdown("---")
    st.subheader("Translation History")

    for item in reversed(st.session_state.history):

        st.write(f"Original: {item['original']}")

        st.write(
            f"Translated ({item['language']}): "
            f"{item['translated']}"
        )

        st.markdown("---")

#Clear History
if st.button("Clear History"):
    st.session_state.history = []
    st.rerun()
    
# Footer
st.markdown("---")
st.caption("Built with Python + Streamlit")