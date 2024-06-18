import subprocess
import time
import sys
import os

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
        
        # Create log files for each service
        stdout_log = open(f"{service}_stdout.log", "w")
        stderr_log = open(f"{service}_stderr.log", "w")
        
        # Start the process and redirect stdout and stderr to log files
        process = subprocess.Popen(command, stdout=stdout_log, stderr=stderr_log)
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

    # Close log files
    for service in services.keys():
        stdout_log.close()
        stderr_log.close()
