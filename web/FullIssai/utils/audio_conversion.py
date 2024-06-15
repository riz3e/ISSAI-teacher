from pydub import AudioSegment
import soundfile as sf

def convert_audio_to_wav(input_audio_path):
    output_audio_path = input_audio_path.replace('.mp3', '.wav')  # Assuming input might be .mp3
    audio = AudioSegment.from_file(input_audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_audio_path, format="wav")
    return output_audio_path
