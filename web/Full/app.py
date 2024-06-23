# Import necessary libraries
import os
from flask import Flask, request, jsonify, send_file, render_template
import requests
import io

# Initialize Flask app
app = Flask(__name__)

# Microservice URLs (replace with your actual URLs)
TRANSCRIBE_SERVICE_URL = "http://localhost:5001/transcribe"
TTS_SERVICE_URL = "http://localhost:5002/generate_audio"
SUMMARY_API_URL = "http://localhost:5003/summarize"
GPT_CHAT_URL = "http://localhost:5004/chat"

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML template

@app.route('/conversation')
def conversation():
    return render_template('gpt.html')  # Render the HTML template

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio-file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['audio-file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Forward the request to the transcribe microservice
        files = {'file': (file.filename, file.stream, file.content_type)}
        response = requests.post(TRANSCRIBE_SERVICE_URL, files=files)
        response.raise_for_status()
        transcription = response.json().get('transcription', '')
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to transcription service: {str(e)}'}), 500
    except KeyError:
        return jsonify({'error': 'Invalid response from transcription service'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'transcription': transcription})

@app.route('/gpt', methods=['POST'])
def gpt():
    user_input = request.json.get('user_input')  # Assuming user_input is sent as JSON
    conversation_history = request.json.get('conversation_history')
    try:

        response = requests.post(GPT_CHAT_URL, json={'user_input': user_input, 'conversation_history': conversation_history})
        response.raise_for_status()
        gpt_response = response.json().get('response')
        conversation_history = response.json().get('conversation_history')
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to GPT service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'response': gpt_response,
                    'conversation_history': conversation_history})


# @app.route('/gpt/create_client', methods=['POST'])
# def gpt():
#     return jsonify({"message": "yes"})


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': "Empty!"}), 400

    try:
        response = requests.post(SUMMARY_API_URL, data={'text': text})
        response.raise_for_status()
        response_data = response.json()
        summary_text = response_data.get("text")
        summary_text2 = response_data.get("summary")
        print(response_data)
        print(summary_text, summary_text2)
       
    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to Summary service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'summary': summary_text2})

async def translateText(text: str, From: str, to: str) -> str:
    # Define the URL and the parameters
    url = "https://issai.nu.edu.kz/tilmash/"
    params = {
        'translate': 'true',
        'from': From, #   'kaz_Cyrl'
        'to': to,   #   'eng_Latn'
        'text': text
    }

    try:
        # Send the GET request
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Return the response text
            return response.text
        else:
            # Return an error message
            return f"Error: Unable to translate text. Status code: {response.status_code}"
    except requests.RequestException as e:
        # Return an error message if there was an exception
        return f"Error: An exception occurred - {e}"

@app.route('/translate', methods=['POST'])
def translate_handler():
    try:
        data = request.get_json()
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        translated_text = translate_text(text, 'kaz_Cyrl', 'eng_Latn')
        
        return jsonify({"translated_text": translated_text}), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        print("text raw", data)

        if data is None:
            return jsonify({'error': 'No JSON data received'}), 400

        text = data.get('text')

        if text is None:
            return jsonify({'error': 'No "text" field found in JSON data'}), 400

        # Forward the request to the text-to-speech microservice
        response = requests.post(TTS_SERVICE_URL, data={'text': text})
        response.raise_for_status()
        audio_data = response.content
        
        # Return the audio file as response
        return send_file(io.BytesIO(audio_data), as_attachment=True, download_name='output.wav', mimetype='audio/wav')

    except requests.RequestException as e:
        return jsonify({'error': f'Error during request to TTS service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)
