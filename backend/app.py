from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt

app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# Ensure the ./files directory exists
os.makedirs('./files', exist_ok=True)

# Load the saved model
model = keras.models.load_model('../ml/models/model_weights.weights.h5', compile=False)

## Model Params
# Define the same preprocessing parameters used during training
frame_length = 256
frame_step = 160
fft_length = 384

# Define character mapping - this needs to match what you used during training
characters = [x for x in "abcdefghijklmnopqrstuvwxyz' "]
char_to_num = keras.layers.StringLookup(vocabulary=characters, oov_token="")
num_to_char = keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

# Function to decode predictions
def decode_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0]
    result = tf.strings.reduce_join(num_to_char(results[0])).numpy().decode("utf-8")
    return result

# Function to preprocess a single audio file
def preprocess_audio(audio_file_path):
    # Read the audio file
    file = tf.io.read_file(audio_file_path)
    audio, _ = tf.audio.decode_wav(file)
    audio = tf.squeeze(audio, axis=-1)
    audio = tf.cast(audio, tf.float32)

    # Create spectrogram
    spectrogram = tf.signal.stft(
        audio,
        frame_length=frame_length,
        frame_step=frame_step,
        fft_length=fft_length
    )
    spectrogram = tf.abs(spectrogram)
    spectrogram = tf.math.pow(spectrogram, 0.5)

    # Normalize
    means = tf.math.reduce_mean(spectrogram, 1, keepdims=True)
    stddevs = tf.math.reduce_std(spectrogram, 1, keepdims=True)
    spectrogram = (spectrogram - means) / (stddevs + 1e-10)

    # Add batch dimension
    spectrogram = tf.expand_dims(spectrogram, 0)

    return spectrogram

def transcribe_audio(audio_file_path):
    # Preprocess the audio
    input_data = preprocess_audio(audio_file_path)

    # Make prediction
    prediction = model.predict(input_data)

    # Decode the prediction
    transcription = decode_predictions(prediction)

    print("Predicted transcription:")
    print(transcription)
    return "Test"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join('./files', file.filename)
    file.save(file_path)
    transcription = transcribe_audio(file_path)
    os.remove(file_path)

    return jsonify({"transcription": transcription})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
