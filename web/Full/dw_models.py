import os
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, VitsModel, AutoTokenizer

def download_and_save_wav2vec2(model_name: str, processor_name: str, save_directory: str):
    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)
    
    # Load and save the Wav2Vec2 model and processor
    processor = Wav2Vec2Processor.from_pretrained(processor_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name)

    processor.save_pretrained(save_directory)
    model.save_pretrained(save_directory)
    
    print(f"Wav2Vec2 model and processor saved to {save_directory}")

def download_and_save_vits(model_name: str, tokenizer_name: str, save_directory: str):
    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)
    
    # Load and save the Vits model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    model = VitsModel.from_pretrained(model_name)

    tokenizer.save_pretrained(save_directory)
    model.save_pretrained(save_directory)
    
    print(f"Vits model and tokenizer saved to {save_directory}")

if __name__ == "__main__":
    # Directories to save the models
    wav2vec2_save_dir = "wav2vec2_model"
    vits_save_dir = "vits_model"

    # Download and save Wav2Vec2 model and processor
    download_and_save_wav2vec2("aismlv/wav2vec2-large-xlsr-kazakh", "aismlv/wav2vec2-large-xlsr-kazakh", wav2vec2_save_dir)

    # Download and save Vits model and tokenizer
    download_and_save_vits("facebook/mms-tts-kaz", "facebook/mms-tts-kaz", vits_save_dir)
