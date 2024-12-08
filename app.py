
from gtts import gTTS
from flask import Flask, request, jsonify, send_from_directory, Response
import speech_recognition as sr
import io
import os
import tempfile

app = Flask(__name__)

# Configure temporary directory for audio files
temp_dir = tempfile.gettempdir()

@app.route('/convert_audio_to_text', methods=['POST'])
def convert_audio_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=temp_dir) as temp_audio_file:
            file.save(temp_audio_file.name)
            print(f"Audio saved to {temp_audio_file.name}")
            with sr.AudioFile(temp_audio_file.name) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="pt-BR") # Specify language
            os.remove(temp_audio_file.name) # Clean up temporary file.
            return jsonify({"text": text})

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Could not request results from Google Speech Recognition service; {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/convert_text_to_audio', methods=['POST'])
def convert_text_to_audio():
    if 'text' not in request.json:
        return jsonify({"error": "No text provided"}), 400

    text = request.json['text']
    try:
        # Generate audio from text using a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=temp_dir) as temp_audio_file:
            tts = gTTS(text, lang='pt', slow=False)
            tts.save(temp_audio_file.name)
            print(f"Audio saved to {temp_audio_file.name}")

        # Return the audio file using send_from_directory for better security.  Avoids direct path exposure.
        return send_from_directory(temp_dir, os.path.basename(temp_audio_file.name), mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
