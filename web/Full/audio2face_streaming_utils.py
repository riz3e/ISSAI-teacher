import sys
import grpc
import time
import numpy as np
import soundfile

import audio2face_pb2
import audio2face_pb2_grpc


def push_audio_track(url, audio_data, samplerate, instance_name):
    block_until_playback_is_finished = True  # Adjust as necessary
    try:
        with grpc.insecure_channel(url) as channel:
            stub = audio2face_pb2_grpc.Audio2FaceStub(channel)
            request = audio2face_pb2.PushAudioRequest(
                audio_data=audio_data.astype(np.float32).tobytes(),
                samplerate=samplerate,
                instance_name=instance_name,
                block_until_playback_is_finished=block_until_playback_is_finished
            )
            print("Sending audio data...")
            response = stub.PushAudio(request)
            if response.success:
                print("Sent 200")
            else:
                print(f"ERROR: {response.message}")
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
    finally:
        print("Closed channel")


def push_audio_track_stream(url, audio_data, samplerate, instance_name):
    chunk_size = samplerate // 10  # Adjust as necessary
    sleep_between_chunks = 0.01  # Adjust as necessary
    block_until_playback_is_finished = True  # Adjust as necessary

    try:
        with grpc.insecure_channel(url) as channel:
            print("Channel created")
            stub = audio2face_pb2_grpc.Audio2FaceStub(channel)

            def make_generator():
                start_marker = audio2face_pb2.PushAudioStreamRequestStart(
                    samplerate=samplerate,
                    instance_name=instance_name,
                    block_until_playback_is_finished=block_until_playback_is_finished
                )
                yield audio2face_pb2.PushAudioStreamRequest(start_marker=start_marker)
                
                for i in range(len(audio_data) // chunk_size + 1):
                    time.sleep(sleep_between_chunks)
                    chunk = audio_data[i * chunk_size: (i + 1) * chunk_size]
                    yield audio2face_pb2.PushAudioStreamRequest(audio_data=chunk.astype(np.float32).tobytes())

            request_generator = make_generator()
            print("Sending audio data...")
            response = stub.PushAudioStream(request_generator)
            if response.success:
                print("Sent 200")
            else:
                print(f"ERROR: {response.message}")
    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
    finally:
        print("Channel closed")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <url> <audio_file> <samplerate> <instance_name>")
        sys.exit(1)

    url = sys.argv[1]
    audio_file = sys.argv[2]
    samplerate = int(sys.argv[3])
    instance_name = sys.argv[4]

    try:
        audio_data, _ = soundfile.read(audio_file)
        # Choose either push_audio_track or push_audio_track_stream based on your requirement
        push_audio_track(url, audio_data, samplerate, instance_name)
        # push_audio_track_stream(url, audio_data, samplerate, instance_name)
    except Exception as e:
        print(f"Error reading audio file or processing request: {e}")
        sys.exit(1)
