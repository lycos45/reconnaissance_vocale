import os
import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import base64

def transcribe_speech(api, language):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("Parlez maintenant...")
            audio_text = r.listen(source, timeout=10, phrase_time_limit=0)
            st.info("Transcription en cours...")
            if api == "Google":
                text = r.recognize_google(audio_text, language=language)
                return text
    except sr.WaitTimeoutError:
        st.error("Temps d'attente dépassé. Aucune parole détectée.")
        return None
    except sr.RequestError:
        st.error("La requête de reconnaissance vocale a échoué. Vérifiez votre connexion Internet.")
        return None
    except sr.UnknownValueError:
        st.error("Impossible de reconnaître la parole. Veuillez parler plus clairement.")
        return None

def translate_text(text, dest_language):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        st.error(f"Erreur lors de la traduction : {e}")
        return None

def text_to_speech(text, language):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("translated_audio.mp3")
        return "translated_audio.mp3"
    except Exception as e:
        st.error(f"Erreur lors de la synthèse vocale : {e}")
        return None

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
        transcription = transcribe_speech(api, language)
        if transcription:
            st.write("**Transcription :** ", transcription)
            
            # Traduction automatique après la transcription
            translated_text = translate_text(transcription, dest_language)
            if translated_text:
                st.write("**Texte Traduit :** ", translated_text)
                
                # Synthèse vocale après la traduction
                audio_file = text_to_speech(translated_text, dest_language)
                if audio_file:
                    st.success("Traduction vocale prête.")
                    play_audio(audio_file)

    else:
        st.info("Appuyez sur 'Démarrer l'Enregistrement' pour commencer.")

if __name__ == "__main__":
    main()
