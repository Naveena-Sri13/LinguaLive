import streamlit as st
from deep_translator import GoogleTranslator
if "history" not in st.session_state:
    st.session_state.history=[]
st.title("LinguaLive")
st.write("Real-time Multilingual Communication Assisstant")
st.markdown("---")
user_text=st.text_input("Enter your text:")
language = {
    "Tamil":"ta",
    "Hindi":"hi",
    "Spanish":"es",
    "french":"fr"
    }
selected_language = st.selectbox("Choose Target Language:",list(language.keys()))
if st.button("Translate"):
    if user_text.strip()=="":
        st.warning("Please enter some text.")

    else:
        translated=GoogleTranslator(
        source='auto',
        target=language[selected_language]
        ).translate(user_text)


        st.subheader("Translated Text")
        st.success(translated)

        st.session_state.history.append({
            "original":user_text,
            "translated":translated,
            "language":selected_language
        })

if st.session_state.history:
    st.markdown("---")
    st.subheader("Translation History")

    for item in reversed(st.session_state.history):
        st.write(f"Original:{item['original']}")
        st.write(f"Translated({item['language']}):{item['translated']}")
        st.markdown("---")


    st.markdown("---")
    st.caption("Built with Python + Streamlit")