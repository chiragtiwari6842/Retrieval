from flask import Flask, request, render_template, send_file
import os
from pydub import AudioSegment
import librosa
import numpy as np
import simpleaudio as sa

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analyze_audio(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)

    # Calculate audio quality metrics
    noise_level = np.mean(np.abs(y))  # Example noise level assessment
    dynamic_range = np.max(y) - np.min(y)  # Dynamic range
    frequency_response = np.fft.fft(y)  # Frequency response

    # Score (this is a simple scoring system; improve as needed)
    score = (1 - noise_level) * (dynamic_range / np.max(np.abs(y)))

    return {
        'noise_level': noise_level,
        'dynamic_range': dynamic_range,
        'score': score,
        'frequency_response': frequency_response,
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        audio_file = request.files['audio']
        if audio_file:
            file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
            audio_file.save(file_path)

            # Analyze audio quality
            metrics = analyze_audio(file_path)

            # Enhance audio quality (simple example: apply gain)
            audio = AudioSegment.from_file(file_path)
            enhanced_audio = audio + 10  # Increase volume by 10 dB
            enhanced_file_path = os.path.join(UPLOAD_FOLDER, 'enhanced_' + audio_file.filename)
            enhanced_audio.export(enhanced_file_path, format='wav')

            return render_template('index.html', metrics=metrics, enhanced_file_path=enhanced_file_path)

    return render_template('index.html')

@app.route('/play/<filename>')
def play_audio(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    # Load audio data for playback
    y, sr = librosa.load(file_path, sr=None)

    # Convert to numpy array and normalize
    y_normalized = (y * 32767).astype(np.int16)

    # Play audio using simpleaudio
    play_obj = sa.play_buffer(y_normalized, 1, 2, sr)
    play_obj.wait_done()  # Wait until playback is finished
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable
    app.run(host='0.0.0.0', port=port, debug=True)
