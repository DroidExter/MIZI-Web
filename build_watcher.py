"""
A script for monitoring file changes in content and template directories
and automatically running the build process when changes are detected.

This script uses the `watchdog` library to observe changes in specified directories/files and
automatically triggers the build process by running the `build.py` script whenever a file 
is modified, created, or deleted. The build process is executed using the command 
`python build.py`, and any additional command-line arguments passed to `build_watcher.py`
are forwarded to the `build.py` script.

Configuration variables:
- `BASE_DIR`: Base directory where the script is located.
- `PATHS_TO_WATCH`: A tuple of directories to watch for changes (content and templates).
- `build_command`: The command used to execute the build script (`build.py`), with additional arguments passed from the command line.
"""


import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import sys

BASE_DIR = Path(__file__).parent
PATHS_TO_WATCH = (BASE_DIR/'content', BASE_DIR/'templates')

build_command = [sys.executable, 'build.py']

build_command.extend(sys.argv[1:])

print("Running build")
subprocess.run(build_command, check=True)

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return        
        self.run_build_script()

    def on_created(self, event):
        if event.is_directory:
            return
        self.run_build_script()

    def on_deleted(self, event):
        if event.is_directory:
            return
        self.run_build_script()

    def run_build_script(self):
        print("Change detected, running build")
        subprocess.run(build_command, check=True)

def watch_directories():
    event_handler = ChangeHandler()
    observer = Observer()

    for dir_path in PATHS_TO_WATCH:
        observer.schedule(event_handler, str(dir_path), recursive=True)

    observer.start()
    print("Monitoring changes in the folders...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch_directories()
