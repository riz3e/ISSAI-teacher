import subprocess
import time

# Define the command to run each service
services = {
    "app.py": ["python", "app.py"],
    "TTS.py": ["python", "TTS.py"],
    "STT.py": ["python", "STT.py"],
    "ai.py": ["python", "ai.py"]
}

# List to keep track of the processes
processes = []

try:
    # Start each service in the background
    for service, command in services.items():
        print(f"Starting {service}...")
        process = subprocess.Popen(command)
        processes.append(process)
        time.sleep(1)  # Small delay to avoid race conditions on startup
    print("All services have been started.")

    # Keep the main script running while services are active
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("Stopping all services...")
    for process in processes:
        process.terminate()

    for process in processes:
        process.wait()

    print("All services have been stopped.")