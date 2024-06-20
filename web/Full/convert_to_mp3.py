import io
from pydub import AudioSegment

def convert_wav_to_mp3(wav_buffer: io.BytesIO) -> io.BytesIO:
    # Load the WAV buffer into an AudioSegment
    wav_buffer.seek(0)
    audio_segment = AudioSegment.from_wav(wav_buffer)

    # Convert to MP3
    mp3_buffer = io.BytesIO()
    audio_segment.export(mp3_buffer, format="mp3")
    mp3_buffer.seek(0)

    return mp3_buffer
