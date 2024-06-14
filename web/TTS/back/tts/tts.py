# back/tts/tts.py
import torch
from tts.model import TTSModel
import torchaudio
import os

def text_to_speech(text):
    model = TTSModel.load_from_checkpoint("../neuro/g_01720000", "../neuro/EMA_grad_4702.pt")
    model.eval()

    with torch.no_grad():
        audio = model.synthesize(text)

    audio_dir = "back/tts/audio"
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, "output.wav")
    torchaudio.save(audio_path, audio, sample_rate=22050)
    return audio_path
