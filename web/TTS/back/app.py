# back/app.py
from flask import Flask, request, jsonify, render_template, send_file
from tts.tts import text_to_speech

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tts', methods=['POST'])
def tts():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        audio_path = text_to_speech(text)
        return send_file(audio_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
