import os
from flask import Flask, render_template, request, jsonify
from google.cloud import translate_v2 as translate
from google.cloud import speech
from google.cloud import texttospeech


# Initialize Flask application
app = Flask(__name__)

# Initialize Google Cloud clients
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_your_google_cloud_credentials.json'

translate_client = translate.Client()
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()


# Route for home page
@app.route('/')
def index():
    return render_template('index9.html')


# Translation endpoint
@app.route('/translate', methods=['POST'])
def translate_text():
    content = request.json
    input_text = content['text']
    target_language = content['target_language']

    # Detect language if not specified
    result = translate_client.translate(input_text, target_language=target_language)
    translated_text = result['translatedText']

    return jsonify({'translated_text': translated_text})


# Speech-to-Text endpoint
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    audio_file = request.files['audio']
    audio_content = audio_file.read()

    # Perform speech recognition
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US'  # Adjust as needed
    )

    response = speech_client.recognize(config=config, audio=audio)

    # Extract transcription
    transcription = ''
    for result in response.results:
        transcription += result.alternatives[0].transcript

    return jsonify({'transcription': transcription})


# Text-to-Speech endpoint
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    content = request.json
    input_text = content['text']
    output_file = 'output.mp3'  # Adjust filename as needed

    # Perform text-to-speech synthesis
    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US',  # Adjust as needed
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Save synthesized audio to file
    with open(output_file, 'wb') as out:
        out.write(response.audio_content)

    return jsonify({'message': 'Text-to-speech conversion successful'})


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
