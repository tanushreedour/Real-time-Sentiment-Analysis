from dotenv import load_dotenv
from datetime import datetime
import os

# Import namespaces
# Import namespaces
import azure.cognitiveservices.speech as speech_sdk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv("SPEECH_KEY")
        ai_region = os.getenv("SPEECH_REGION")
        lang_endpoint = os.getenv("LANGUAGE_SERVICE_ENDPOINT")
        lang_key = os.getenv("LANGUAGE_SERVICE_KEY")

        # Configure speech service
        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)

        # print("Ready to use speech service in:", speech_config.region)

        # Get spoken input
        command = TranscribeCommand()
        # data = open("sentiment.txt")
        # data.write(str(command))
        print(command)
        print("command type -> ", type(command))

        # write data to command
        with open("sentiment.txt", "w") as f:
            # Write data to the file
            f.write(str(command))
            f.close()

        # sentiment =
        senti = getsentiment(lang_key, lang_endpoint)
        print(senti)

        Telloutput(senti)

    except Exception as ex:
        print(ex)


def getsentiment(lang_key, lang_endpoint):
    credential = AzureKeyCredential(lang_key)
    with open("sentiment.txt", "r") as f:
        text = f.read()
        ai_client = TextAnalyticsClient(endpoint=lang_endpoint, credential=credential)
        sentimentAnalysis = ai_client.analyze_sentiment(documents=[text])[0]
        # print("\nSentiment: {}".format(sentimentAnalysis.sentiment))
        f.close()
        return sentimentAnalysis.sentiment


def TranscribeCommand():
    command = ""

    # Configure speech recognition
    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    print("Speak now...")

    # Process speech input
    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        # print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)
    # Return the command
    return command


def Telloutput(senti):
    response_text = "The sentiment of spoken input  is " + senti

    # Configure speech synthesis
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-GB-LibbyNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    # Synthesize spoken output
    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(response_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    # Print the response
    print(response_text)


if __name__ == "__main__":
    main()
