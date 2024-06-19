import subprocess
import time
import os

#change locally
venv_destination = r"C:\Projs\ISSAI-teacher\venv\Scripts\python.exe"

# Define the command to run each service
services = {
    "app.py": [venv_destination, "app.py"],
    "TTS.py": [venv_destination, "TTS.py"],
    "STT.py": [venv_destination, "STT.py"],
    "ai.py": [venv_destination, "ai.py"]
}

# List to keep track of the processes and log files
processes = []
log_files = {}

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
        log_files[service] = (stdout_log, stderr_log)

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

finally:
    # Close log files
    for service, logs in log_files.items():
        stdout_log, stderr_log = logs
        stdout_log.close()
        stderr_log.close()