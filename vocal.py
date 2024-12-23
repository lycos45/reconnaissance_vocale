import os
import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import sounddevice as sd
import numpy as np
import wave
import base64

# Enregistrement audio avec SoundDevice
def record_audio(filename="output.wav", duration=5, samplerate=44100):
    st.info("Enregistrement en cours...")
    try:
        # Enregistrement audio
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()  # Attendre la fin de l'enregistrement

        # Sauvegarde en tant que fichier WAV
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
        st.success("Enregistrement terminé.")
        return filename
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement : {e}")
        return None

# Transcription de l'audio
def transcribe_speech(filename, api, language):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(filename) as source:
            audio_text = r.record(source)  # Charger l'audio enregistré
            st.info("Transcription en cours...")
            if api == "Google":
                text = r.recognize_google(audio_text, language=language)
                return text
    except sr.RequestError:
        st.error("La requête de reconnaissance vocale a échoué. Vérifiez votre connexion Internet.")
        return None
    except sr.UnknownValueError:
        st.error("Impossible de reconnaître la parole. Veuillez parler plus clairement.")
        return None

# Traduction
def translate_text(text, dest_language):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        st.error(f"Erreur lors de la traduction : {e}")
        return None

# Synthèse vocale
def text_to_speech(text, language):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("translated_audio.mp3")
        return "translated_audio.mp3"
    except Exception as e:
        st.error(f"Erreur lors de la synthèse vocale : {e}")
        return None

# Lecture audio
def play_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio autoplay controls>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    Votre navigateur ne supporte pas l'audio.
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors de la lecture de l'audio : {e}")

# Main
def main():
    st.title("Application de Reconnaissance Vocale et Traduction")
    
    # Sélection de l'API de reconnaissance vocale
    api = st.selectbox("Sélectionnez l'API de Reconnaissance Vocale", ["Google"])
    
    # Sélection de la langue pour la transcription
    language = st.selectbox("Sélectionnez la Langue pour la Transcription", ["fr-FR", "en-US", "zh-CN", "ko-KR"])
    
    # Sélection de la langue cible pour la traduction
    dest_language = st.selectbox("Sélectionnez la Langue de Traduction", ["en", "fr", "es", "de", "zh-cn", "ko"])
    
    # Bouton pour démarrer l'enregistrement
    record_button = st.button("Démarrer l'Enregistrement")
    
    if record_button:
        audio_file = record_audio(duration=5)
        if audio_file:
            transcription = transcribe_speech(audio_file, api, language)
            if transcription:
                st.write("**Transcription :** ", transcription)
                
                # Traduction automatique après la transcription
                translated_text = translate_text(transcription, dest_language)
                if translated_text:
                    st.write("**Texte Traduit :** ", translated_text)
                    
                    # Synthèse vocale après la traduction
                    audio_output = text_to_speech(translated_text, dest_language)
                    if audio_output:
                        st.success("Traduction vocale prête.")
                        play_audio(audio_output)

if __name__ == "__main__":
    main()
