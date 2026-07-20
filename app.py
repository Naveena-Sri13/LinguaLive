import streamlit as st
import streamlit.components.v1 as components
import pyperclip

from translator import (
    translate_text,
    translate_for_call,
    detect_language_key,
    TranslationError,
)


from streamlit_mic_recorder import mic_recorder
from datetime import datetime

import os
import json

from config import (
    settings,
    CONTACTS_FILE,
    RECENT_CALLS_FILE,
    SUPPORTED_LANGUAGES,
    get_language,
)
languages = {
    lang.display_name: lang.translate_code
    for lang in SUPPORTED_LANGUAGES.values()
}

live_languages = list(languages.keys())

from storage import (
    ensure_data_folder,
    load_json_file,
    save_json_file
)

from speech import (
    transcribe_audio_bytes,
    synthesize_speech_bytes,
    SpeechError
)




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

if "live_session_active" not in st.session_state:
    st.session_state.live_session_active=False

if "session_speaking_language" not in st.session_state:
    st.session_state.session_speaking_language=""

if "session_hearing_language" not in st.session_state:
    st.session_state.session_hearing_language=""

if "session_contact" not in st.session_state:
    st.session_state.session_contact=""

if "saved_contacts" not in st.session_state:
    st.session_state.saved_contacts=load_json_file(
        CONTACTS_FILE,
        []
    )

if "recent_calls" not in st.session_state:
    st.session_state.recent_calls=load_json_file(
        RECENT_CALLS_FILE,
        []
    )

if "call_started_at" not in st.session_state:
    st.session_state.call_started_at=None

if "call_status" not in st.session_state:
    st.session_state.call_status="idle"

if "live_talk_active" not in st.session_state:
    st.session_state.live_talk_active=False

if "live_voice_audio_bytes" not in st.session_state:
    st.session_state.live_voice_audio_bytes=None

if "live_detected_speech" not in st.session_state:
    st.session_state.live_detected_speech=""

if "live_translated_text" not in st.session_state:
    st.session_state.live_translated_text=""

if "live_target_lang_code" not in st.session_state:
    st.session_state.live_target_lang_code=""

if "live_translation_audio" not in st.session_state:
    st.session_state.live_translation_audio=None

if "live_current_turn" not in st.session_state:
    st.session_state.live_current_turn="you"

if "live_detected_label" not in st.session_state:
    st.session_state.live_detected_label=""

if "live_translated_label" not in st.session_state:
    st.session_state.live_translated_label=""

default_text=""


if "reuse_text" in st.session_state:

    default_text=st.session_state["reuse_text"]

    del st.session_state["reuse_text"]


# ---------------- SPEECH TO TEXT ----------------

def use_detected_speech():

    st.session_state.text_input_value=(
        st.session_state.detected_speech_text
    )

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
LinguaLive is a **real-time multilingual voice communication platform**.

It helps people speak naturally in their own language while the listener hears the message in their preferred language.
""")

    st.markdown("---")

    st.subheader("⚡ Current Capabilities")

    st.markdown("""
✅ Text → Text Translation  

✅ Text → Speech  

✅ Speech → Text   

✅ Speech → Speech  

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

st.markdown(
    "### Choose LinguaLive Mode"
)

st.caption(
    "Start a multilingual live session, or use the assistant to translate and test speech features."
)

mode=st.radio(

    "Select one:",

    [

        "Live Communication",
        "Translation Assistant"

    ]

)

# ======================================================
# LIVE COMMUNICATION MODE
# ======================================================

if mode=="Live Communication":

    if not st.session_state.live_session_active:

        st.subheader(
            "📞 Live Communication"
        )

        call_tab,contacts_tab,history_tab=st.tabs(
            [
                "📞 Start New Call",
                "👥 Contacts",
                "🕒 Recent Calls"
            ]
        )

        # ---------------- START NEW CALL TAB ----------------

        with call_tab:

            st.info(
                "Set up the call once. LinguaLive will use these session languages during the call."
            )

            st.markdown(
                "### 👤 Contact"
            )

            contact_input=st.text_input(
                "Enter contact name or number:",
                placeholder="Example: Amma, Friend, +91..."
            )

            my_language=st.selectbox(
                "You Speak:",
                live_languages,
                key="my_language"
            )

            hear_language=st.selectbox(
                "They Speak:",
                live_languages,
                key="hear_language"
            )

            st.success(

f"""
Calling: {contact_input if contact_input else "New Contact"}

You Speak: {my_language}

They Speak: {hear_language}
"""

            )

            if st.button(
                "🟢 Start Call",
                key="start_new_call",
                use_container_width=True
            ):

                st.session_state.live_session_active=True
                st.session_state.live_talk_active=False

                st.session_state.session_contact=(
                    contact_input.strip()
                    if contact_input.strip()
                    else "New Contact"
                )

                st.session_state.session_speaking_language=my_language
                st.session_state.session_hearing_language=hear_language
                st.session_state.call_started_at=datetime.now()
                st.session_state.call_status="calling"

                st.session_state.live_detected_speech=""
                st.session_state.live_translated_text=""
                st.session_state.live_voice_audio_bytes=None
                st.session_state.live_translation_audio=None
                st.session_state.live_detected_label=""
                st.session_state.live_translated_label=""
                st.session_state.live_current_turn="you"

                st.rerun()

        # ---------------- CONTACTS TAB ----------------

        with contacts_tab:

           st.markdown("## 👥 Contacts")

           st.caption(
        "Save contacts and quickly start multilingual conversations."
    )

    # ---------------------------------------------------
    # Add Contact
    # ---------------------------------------------------

    with st.expander(
        "➕ Add New Contact",
        expanded=True
    ):

        with st.form(
            "add_contact_form",
            clear_on_submit=True
        ):

            contact_name = st.text_input(
                "👤 Contact Name",
                placeholder="Example: Rohith"
            )

            contact_number = st.text_input(
                "📞 Phone Number",
                placeholder="+91 XXXXX XXXXX"
            )

            contact_language = st.selectbox(
                "🌐 Preferred Language",
                live_languages,
                key="new_contact_language"
            )

            save_contact = st.form_submit_button(
                "Save Contact",
                use_container_width=True
            )

        if save_contact:

            if (
                contact_name.strip() == ""
                and
                contact_number.strip() == ""
            ):

                st.warning(
                    "Please enter at least a contact name or phone number."
                )

            else:

                st.session_state.saved_contacts.append(

                    {

                        "name":
                        contact_name.strip()
                        if contact_name.strip()
                        else "Unnamed Contact",

                        "number":
                        contact_number.strip()
                        if contact_number.strip()
                        else "No Number",

                        "language":
                        contact_language

                    }

                )

                save_json_file(
                    CONTACTS_FILE,
                    st.session_state.saved_contacts
                )

                st.success(
                    "Contact saved successfully."
                )

                st.rerun()

    st.divider()

    # ---------------------------------------------------
    # Call Settings
    # ---------------------------------------------------

    st.markdown("### 📞 Start a Call")

    contact_call_language = st.selectbox(
        "🌐 Your Language",
        live_languages,
        key="contact_call_language"
    )

    st.divider()

    # ---------------------------------------------------
    # Saved Contacts
    # ---------------------------------------------------

    st.markdown("### 📒 Saved Contacts")

    if st.session_state.saved_contacts:

        for index, contact in enumerate(
            st.session_state.saved_contacts
        ):

            st.markdown(
                f"""
### 👤 {contact['name']}

📞 **{contact['number']}**

🌐 **{contact['language']}**
"""
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "📞 Call",
                    key=f"call_contact_{index}",
                    use_container_width=True
                ):

                    st.session_state.live_session_active = True
                    st.session_state.live_talk_active = False

                    st.session_state.session_contact = contact["name"]

                    st.session_state.session_speaking_language = (
                        contact_call_language
                    )

                    st.session_state.session_hearing_language = (
                        contact["language"]
                    )

                    st.session_state.call_started_at = datetime.now()

                    st.session_state.call_status = "calling"

                    st.session_state.live_detected_speech = ""
                    st.session_state.live_translated_text = ""
                    st.session_state.live_translation_audio = None
                    st.session_state.live_voice_audio_bytes = None

                    st.session_state.live_current_turn = "you"

                    st.rerun()

            with col2:

                if st.button(
                    "🗑 Delete",
                    key=f"delete_contact_{index}",
                    use_container_width=True
                ):

                    del st.session_state.saved_contacts[
                        index
                    ]

                    save_json_file(
                        CONTACTS_FILE,
                        st.session_state.saved_contacts
                    )

                    st.success(
                        "Contact deleted."
                    )

                    st.rerun()

            with st.expander(
                "✏️ Edit Contact",
                expanded=False
            ):

                with st.form(
                    f"edit_contact_form_{index}"
                ):

                    updated_name = st.text_input(
                        "👤 Contact Name",
                        value=contact["name"],
                        key=f"edit_name_{index}"
                    )

                    updated_number = st.text_input(
                        "📞 Phone Number",
                        value=contact["number"],
                        key=f"edit_number_{index}"
                    )

                    updated_language = st.selectbox(
                        "🌐 Preferred Language",
                        live_languages,
                        index=(
                            live_languages.index(
                                contact["language"]
                            )
                            if contact["language"] in live_languages
                            else 0
                        ),
                        key=f"edit_language_{index}"
                    )

                    update_contact = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True
                    )

                if update_contact:

                    st.session_state.saved_contacts[index] = {

                        "name":
                        updated_name.strip()
                        if updated_name.strip()
                        else "Unnamed Contact",

                        "number":
                        updated_number.strip()
                        if updated_number.strip()
                        else "No Number",

                        "language":
                        updated_language

                    }

                    save_json_file(
                        CONTACTS_FILE,
                        st.session_state.saved_contacts
                    )

                    st.success(
                        "Contact updated."
                    )

                    st.rerun()

            st.divider()

    else:

        st.caption(
            "No contacts saved yet."
        )

# ---------------- RECENT CALLS TAB ----------------

        with history_tab:

            st.markdown(
                "### 🕒 Recent Calls"
            )

            if st.session_state.recent_calls:

                for index, call in enumerate(
                    st.session_state.recent_calls
                ):

                    duration_seconds = call[
                        "duration_seconds"
                    ]

                    minutes = duration_seconds // 60
                    seconds = duration_seconds % 60

                    st.info(

f"""
**{call['contact']}**

Ended: {call['ended_at']}

Duration: {minutes:02d}:{seconds:02d}

You Speak: {call['you_speak']}

They Speak: {call['they_speak']}
"""

                    )

                    if st.button(
                        f"📞 Call Again - {call['contact']}",
                        key=f"call_again_{index}",
                        use_container_width=True
                    ):

                        st.session_state.live_session_active = True
                        st.session_state.live_talk_active = False

                        st.session_state.session_contact = call[
                            "contact"
                        ]

                        st.session_state.session_speaking_language = call[
                            "you_speak"
                        ]

                        st.session_state.session_hearing_language = call[
                            "they_speak"
                        ]

                        st.session_state.call_started_at = datetime.now()

                        st.session_state.live_detected_speech = ""
                        st.session_state.live_translated_text = ""
                        st.session_state.live_voice_audio_bytes = None
                        st.session_state.live_translation_audio = None
                        st.session_state.live_detected_label = ""
                        st.session_state.live_translated_label = ""
                        st.session_state.live_current_turn = "you"

                        st.rerun()

                    if st.button(
                        f"🗑️ Delete Call - {call['contact']}",
                        key=f"delete_recent_call_{index}",
                        use_container_width=True
                    ):

                        del st.session_state.recent_calls[
                            index
                        ]

                        save_json_file(
                            RECENT_CALLS_FILE,
                            st.session_state.recent_calls
                        )

                        st.success(
                            "Recent call deleted ✅"
                        )

                        st.rerun()
            else:

                st.caption(
                    "No recent calls yet."
                )
                  

# ======================================================
# TRANSLATION ASSISTANT MODE
# ======================================================

else:

    if st.session_state.detected_speech_text!="":
        st.session_state.text_input_value=(
        st.session_state.detected_speech_text
    )
        
    text_length=len(
    st.session_state.text_input_value
)

    if text_length < 50:
        dynamic_height = 35

    elif text_length < 150:
        dynamic_height = 80

    else:
        dynamic_height = min(
        220,
        80 + (text_length // 20)
    )

    user_text=st.text_area(
    "Enter or edit your text:",
    key="text_input_value",
    height=dynamic_height
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

        st.session_state.detected_speech_text=""
        st.session_state.translated=""
        st.session_state.detected_language=""
        st.session_state.selected_lang_code=""

        st.success(
            "Voice recorded. Click Convert Speech to Text 🎤"
        )


    if st.session_state.voice_audio_bytes:

        if st.button(
            "🎙 Convert Speech to Text"
        ):
            try:
                transcription = transcribe_audio_bytes(
                    st.session_state.voice_audio_bytes,
        "webm",
        st.session_state.selected_language.lower()
    )

                speech_text = transcription.text
            except SpeechError:
                speech_text = None

            

            if speech_text:

                st.session_state.detected_speech_text=speech_text

                st.rerun()

            else:

                st.warning(
                    "Could not recognize speech. Try speaking closer to the microphone!"
                )


    if st.session_state.detected_speech_text:

        st.success(
            f"Detected Speech: {st.session_state.detected_speech_text}"
        )

        if st.button(
            "Clear Speech"
        ):

            st.session_state.detected_speech_text=""
            st.session_state.text_input_value=""

            st.rerun()


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

        code = detect_language_key(
    st.session_state.text_input_value
)

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
        if st.session_state.text_input_value.strip() == "":
            st.warning(
            "Please enter text."
        )

        else:
            try:
                result = translate_text(
        text=st.session_state.text_input_value,
        target_language_key=selected_language.lower(),
    )

                st.session_state.translated = result.translated_text
                st.session_state.detected_language = result.source_language_key
                st.session_state.selected_lang_code = (
        get_language(result.target_language_key).tts_code
    )

            except TranslationError as exc:
                st.error(str(exc))
                st.stop()

            st.session_state.history.append({

            "original":
            st.session_state.text_input_value,

            "translated":
            result.translated_text,

            "language":
            selected_language,

            "time":
            datetime.now().strftime(
                "%H:%M:%S"
            )

        })
            
        if st.session_state.translated:

            st.markdown(

        f"🌐 Detected Language: {st.session_state.detected_language}"

    )
            col1, col2, col3 = st.columns(
        [8, 1, 1]
    )

            with col1:
                st.success(
            st.session_state.translated
        )

            with col2:
                if st.session_state.voice_audio_bytes:
                    st.audio(
            st.session_state.voice_audio_bytes,
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
                "🕒 Recent Translation History"
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