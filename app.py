import streamlit as st
from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speech_sdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Load environment variables
load_dotenv()

# Configuration settings
speech_key = os.getenv("SPEECH_KEY")
speech_region = os.getenv("SPEECH_REGION")
lang_endpoint = os.getenv("LANGUAGE_SERVICE_ENDPOINT")
lang_key = os.getenv("LANGUAGE_SERVICE_KEY")

# Initialize Speech SDK Configuration
speech_config = speech_sdk.SpeechConfig(subscription=speech_key, region=speech_region)

# Streamlit UI setup
st.set_page_config(page_title="Speech Sentiment Analyzer", page_icon="🗣️", layout="wide")

st.markdown("<h1 style='text-align: center;'>🗣️ Speech Sentiment Analyzer 🎙️</h1>", unsafe_allow_html=True)
st.write("")
st.subheader("Speak into your microphone and let AI analyze your sentiment in real-time.")

# Sidebar for instructions
st.sidebar.title("How it Works")
st.sidebar.markdown("""
1. Click the 'Start Recording' button below.
2. Speak into your microphone.
3. The app will transcribe your speech and analyze the sentiment.
4. It will display the sentiment result and also speak it out loud.
""")

# Function to transcribe speech using Azure Speech SDK
def transcribe_speech():
    try:
        # Configure speech recognition
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # Capture speech
        result = recognizer.recognize_once_async().get()
        
        if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
            return result.text
        else:
            return None
    except Exception as e:
        st.error(f"Error during speech recognition: {str(e)}")
        return None
    
# Function to perform sentiment analysis using Azure Text Analytics
def get_sentiment(transcribed_text):
    try:
        client = TextAnalyticsClient(endpoint=lang_endpoint, credential=AzureKeyCredential(lang_key))
        response = client.analyze_sentiment(documents=[transcribed_text])[0]
        return response.sentiment
    except Exception as e:
        st.error(f"Error during sentiment analysis: {str(e)}")
        return None

# Function to speak out the sentiment using Azure Speech SDK
def speak_out(sentiment_result):
    try:
        # Prepare the text-to-speech response based on sentiment
        response_text = f"The sentiment of your speech is {sentiment_result}."
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
        synthesizer.speak_text_async(response_text).get()
    except Exception as e:
        st.error(f"Error during speech synthesis: {str(e)}")

# Main Interface: Start Recording Button
def main():
    st.subheader("")
    if st.button("🎤 Start Recording"):
        with st.spinner('Listening...'):
            transcribed_text = transcribe_speech()
        
        if transcribed_text:
            st.success("Speech recognized successfully!")
            st.write("**Transcribed Text:**", transcribed_text)
            
            # Perform sentiment analysis
            sentiment_result = get_sentiment(transcribed_text)
            
            # Display sentiment result
            if sentiment_result == "positive":
                st.markdown("<h3 style='color:green;'>😊 Positive Sentiment</h3>", unsafe_allow_html=True)
            elif sentiment_result == "neutral":
                st.markdown("<h3 style='color:orange;'>😐 Neutral Sentiment</h3>", unsafe_allow_html=True)
            else:
                st.markdown("<h3 style='color:red;'>😢 Negative Sentiment</h3>", unsafe_allow_html=True)
            
            # Speak out the sentiment result
            speak_out(sentiment_result)
        else:
            st.error("Failed to recognize speech. Please try again.")

if __name__ == "__main__":
    main()