import os
from functools import partial

from piper import Piper, tts  # Import required classes from piper

def generate_speech(text, model_path="./piper/voice-kk-issai-high/kk-issai-high.onnx", speaker_id=4):
    """Generates speech from text using PiperTTS.

    Args:
        text (str): The text string to be converted to speech.
        model_path (str, optional): Path to the piperTTS model (ONNX file). Defaults to "./piper/voice-kk-issai-high/kk-issai-high.onnx".
        speaker_id (int, optional): ID of the speaker voice to use (if the model supports multiple speakers). Defaults to 4.

    Returns:
        str: The path to the generated audio file (output.wav) or None on error.
    """

    output_path = "output.wav"

    try:
        # Create Piper instance with the specified model
        voice = Piper(model_path)

        # Pre-configure speaker ID for efficiency
        synthesize = partial(voice.synthesize, speaker_id=speaker_id)

        # Use the corrected function `tts.synthesize_to_file`
        tts.synthesize_to_file(synthesize(text), output_path)

    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

    if os.path.exists(output_path):
        return output_path
    else:
        print("Error: Generated audio file not found.")
        return None

# Example usage
text = "This is an example text for speech generation."
speech_path = generate_speech(text)

if speech_path:
    print(f"Speech generated successfully! Path: {speech_path}")
else:
    print("Speech generation failed.")
