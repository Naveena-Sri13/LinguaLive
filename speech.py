import streamlit as st

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

    os.environ["PATH"] += (
        os.pathsep
        + FFMPEG_PATH
    )


def speech_to_text(
    audio_bytes,
    language_code="en-IN"
):

    recognizer = sr.Recognizer()

    try:

        audio = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="webm"
        )

        audio = audio.set_channels(
            1
        ).set_frame_rate(
            16000
        )

        wav_io = io.BytesIO()

        audio.export(
            wav_io,
            format="wav"
        )

        wav_io.seek(0)

        with sr.AudioFile(
            wav_io
        ) as source:

            audio_data = recognizer.record(
                source
            )

        text = recognizer.recognize_google(
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