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

if FFMPEG_PATH not in os.environ["PATH"]:
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

if "live_session_active" not in st.session_state:
    st.session_state.live_session_active=False

if "session_speaking_language" not in st.session_state:
    st.session_state.session_speaking_language=""

if "session_hearing_language" not in st.session_state:
    st.session_state.session_hearing_language=""

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

speech_languages={
    "English":"en-IN",
    "Tamil":"ta-IN",
    "Hindi":"hi-IN",
    "Telugu":"te-IN",
    "Malayalam":"ml-IN",
    "Kannada":"kn-IN",
    "French":"fr-FR",
    "Spanish":"es-ES",
    "German":"de-DE"
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


def speech_to_text(audio_bytes, language_code="en-IN"):

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
    audio_data,
    language=language_code
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

    if not st.session_state.live_session_active:

        st.subheader(
            "📞 Start Live Communication"
        )

        st.info(
            "Set up the call by choosing your language and the other person's language. "
            "LinguaLive will translate each spoken message so both people can understand each other."
        )

        my_language=st.selectbox(

            "You Speak:",

            list(
                languages.keys()
            ),

            key="my_language"

        )

        hear_language=st.selectbox(

            "They Speak:",

            list(
                languages.keys()
            ),

            key="hear_language"

        )

        st.success(

f"""
You Speak: {my_language}

They Speak: {hear_language}
"""

        )

        if st.button(

            "🟢 Start Session",
            use_container_width=True

        ):

            st.session_state.live_session_active=True
            st.session_state.live_talk_active=False

            st.session_state.session_speaking_language=my_language
            st.session_state.session_hearing_language=hear_language

            st.session_state.live_detected_speech=""
            st.session_state.live_translated_text=""
            st.session_state.live_voice_audio_bytes=None
            st.session_state.live_translation_audio=None
            st.session_state.live_current_turn="you"

            st.rerun()

    else:

        st.subheader(
            "📞 Live Call"
        )

        st.success(
            "Call Session Active ✅"
        )

        if st.session_state.live_current_turn=="you":

            current_speaker_language=st.session_state.session_speaking_language
            current_target_language=st.session_state.session_hearing_language
            current_turn_text="You speak → They hear"
            detected_label="You said"
            translated_label="They hear"
            push_button_label="🎤 Push to Talk — You Speak"
            release_button_label="⏹ Translate for Them"
            listening_message="🎤 Listening to you..."

        else:

            current_speaker_language=st.session_state.session_hearing_language
            current_target_language=st.session_state.session_speaking_language
            current_turn_text="They speak → You hear"
            detected_label="They said"
            translated_label="You hear"
            push_button_label="🎤 Push to Talk — They Speak"
            release_button_label="⏹ Translate for You"
            listening_message="🎤 Listening to the other person..."

        st.markdown(

f"""
🎧 Call Languages

You Speak: {st.session_state.session_speaking_language}

They Speak: {st.session_state.session_hearing_language}

Current Turn: **{current_turn_text}**

Press **Push to Talk**, speak, then release to translate.
"""

        )

        if not st.session_state.live_talk_active:

            col1,col2=st.columns(2)

            with col1:

                if st.button(
                    "🙋 You Speak",
                    use_container_width=True
                ):

                    st.session_state.live_current_turn="you"
                    st.session_state.live_detected_speech=""
                    st.session_state.live_translated_text=""
                    st.session_state.live_translation_audio=None

                    st.rerun()

            with col2:

                if st.button(
                    "👥 They Speak",
                    use_container_width=True
                ):

                    st.session_state.live_current_turn="they"
                    st.session_state.live_detected_speech=""
                    st.session_state.live_translated_text=""
                    st.session_state.live_translation_audio=None

                    st.rerun()

        

        if not st.session_state.live_talk_active:

            if st.button(
                push_button_label,
                use_container_width=True
            ):

                st.session_state.live_talk_active=True
                st.session_state.live_detected_speech=""
                st.session_state.live_translated_text=""
                st.session_state.live_translation_audio=None

                st.rerun()

        else:

            st.info(
                listening_message
            )

            live_voice_data=mic_recorder(

                start_prompt="Start Recording",

                stop_prompt="Stop Recording",

                key="live_recorder"

            )

            if live_voice_data and "bytes" in live_voice_data:

                st.session_state.live_voice_audio_bytes=live_voice_data[
                    "bytes"
                ]

                st.success(
                    "Live voice recorded ✅"
                )

                live_text=speech_to_text(

                    st.session_state.live_voice_audio_bytes,

                    speech_languages[
                        current_speaker_language
                    ]

                )

                if live_text:

                    st.session_state.live_detected_speech=live_text

                else:

                    st.warning(
                        "Could not recognize live speech. Try speaking closer to the mic."
                    )

            if st.session_state.live_detected_speech:

                st.success(

f"{detected_label}: {st.session_state.live_detected_speech}"

                )
                

            if st.button(
                release_button_label,
                use_container_width=True
            ):

                if st.session_state.live_detected_speech:

                    try:

                        translated=GoogleTranslator(

                            source="auto",

                            target=languages[
                                current_target_language
                            ]

                        

                        ).translate(

                            st.session_state.live_detected_speech

                        )

                        st.session_state.live_translated_text=translated

                        st.session_state.live_target_lang_code=(

                            languages[
                                current_target_language
                            ]

                        )

                        tts=gTTS(

                            text=st.session_state.live_translated_text,

                            lang=st.session_state.live_target_lang_code

                        )

                        tts.save(
                            "live_translation.mp3"
                        )

                        with open(

                            "live_translation.mp3",

                            "rb"

                        ) as file:

                            st.session_state.live_translation_audio=file.read()

                    except Exception as e:

                        st.error(
                            f"Live translation failed: {e}"
                        )

                st.session_state.live_talk_active=False

                st.rerun()

        if st.session_state.live_translated_text:

            st.success(

f"{translated_label}: {st.session_state.live_translated_text}"

            )

        if st.session_state.live_translation_audio:

            st.audio(
                st.session_state.live_translation_audio,
                format="audio/mp3",
                autoplay=True
            )

        if st.button(

            "🔴 End Session",
            use_container_width=True

        ):

            st.session_state.live_session_active=False
            st.session_state.live_talk_active=False

            st.session_state.session_speaking_language=""
            st.session_state.session_hearing_language=""

            st.session_state.live_detected_speech=""
            st.session_state.live_translated_text=""
            st.session_state.live_voice_audio_bytes=None
            st.session_state.live_translation_audio=None
            st.session_state.live_current_turn="you"

            st.rerun()                

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

            speech_text=speech_to_text(
                st.session_state.voice_audio_bytes
            )

            if speech_text:

                st.session_state.detected_speech_text=speech_text

                st.rerun()

            else:

                st.warning(
                    "Could not recognize speech. Try speaking closer to mic!"
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

        if st.session_state.text_input_value.strip()=="":

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