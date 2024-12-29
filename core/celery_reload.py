import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}, restarting Celery worker...")
            restart_celery()

def restart_celery():
    # Restart the Celery worker (modify this as needed for your setup)
    subprocess.run(['celery', '-A', 'app', 'worker', '--loglevel=info'])

def start_watching():
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./tasks.pycd "', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
