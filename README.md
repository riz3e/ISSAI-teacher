# AI-Teacher

This project is an AI-Teacher conversation system that integrates speech recognition, natural language processing, text-to-speech, and 3D avatar animation.

## Components

1. `a2f.py`: Handles audio processing and interaction with the Audio2Face streaming API.
2. `app.py`: The main Flask application serving as the central hub for various services.
3. `gpt.py`: Manages interactions with the GPT model for generating responses.
4. `test.py`: A test script for voice recognition and interaction with the system.
5. `TTS.py`: Handles text-to-speech conversion using OpenAI's API.

## Requirements

- Python 3.12.x
- Virtual environment (venv)
- Various Python packages (specified in requirements.txt)
- Local Vosk model for speech recognition: [Link]()
- .env file for API keys and configurations [Link]()

## Setup Tutorial

1. Install Python 3.12.x from the [official Python website](https://www.python.org/downloads/).

2. Set up a virtual environment:

   ```
   python -m venv venv
   ```

   For more information on virtual environments, refer to the [Python venv documentation](https://docs.python.org/3/library/venv.html).

3. Activate the virtual environment:

   - On Windows:
     in CMD, not PowerShell
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

5. Download the necessary local model and .env file (links to be provided later).

## Running the Application

To run the different components, open separate terminal windows or command prompts for each:

1. Main application:

   ```
   python web/Full/app.py
   ```

2. GPT service:

   ```
   python web/Full/gpt.py
   ```

3. Text-to-Speech service:

   ```
   python web/Full/TTS.py
   ```

4. Audio2Face service:

   ```
   python web/Full/a2f.py
   ```

5. For testing voice recognition:
   ```
   python web/Full/test.py
   ```

Ensure all services are running before attempting to use the full system.

## Note

Make sure to have the local Vosk model installed and the .env file properly configured with necessary API keys before running the application. Links for downloading these will be provided separately.

# System

![system](https://github.com/riz3e/ISSAI-teacher/assets/61588258/8669a3b3-a603-4d6e-89ca-9ab4c0037868)
