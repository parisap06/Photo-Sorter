import os
import shutil
from datetime import datetime
import mimetypes
import time
import pystray
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import threading

print("Script started")
# Define a function to get all media files in a directory and its subdirectories
def get_media_files(directory):
    media_files = []
    mime = mimetypes.MimeTypes()
    mime.add_type('image/heif', '.heif')
    mime.add_type('image/heif-sequence', '.heifs')
    mime.add_type('image/heic', '.heic')
    mime.add_type('image/heic-sequence', '.heics')
    mime.add_type('image/webp', '.webp')
    mime.add_type('video/hevc', '.hevc')
    mime.add_type('video/hevc-sequence', '.hevcs')
    for root, dirs, files in os.walk(directory):
        for filename in files:
            mime_type, _ = mime.guess_type(filename)
            if mime_type is not None and (mime_type.startswith('image') or mime_type.startswith('video')):
                file_path = os.path.join(root, filename)
                if not file_path.startswith(sorted_media_directory):
                    media_files.append(file_path)
    return media_files

# Define the root directory to sort through
root_directory = None
def choose_directory():
    global root_directory
    root_directory = filedialog.askdirectory()
    root_directory_var.set(root_directory)
    sort_existing_media_files_thread = threading.Thread(target=sort_existing_media_files)
    sort_existing_media_files_thread.start()
    monitor_directory_thread = threading.Thread(target=monitor_directory)
    monitor_directory_thread.start()

# Create the GUI for selecting the root directory
root = tk.Tk()
root.title("Photo Sorter")
root_directory_var = tk.StringVar()
root_directory_label = tk.Label(root, text="Root Directory: ")
root_directory_label.pack(side=tk.LEFT)
root_directory_entry = tk.Entry(root, textvariable=root_directory_var, width=50)
root_directory_entry.pack(side=tk.LEFT)
choose_directory_button = tk.Button(root, text="Browse", command=choose_directory)
choose_directory_button.pack(side=tk.LEFT)
root.mainloop()

# Define the directory to store sorted media files
sorted_media_directory = os.path.join(root_directory, "Media")

# Create the directory if it doesn't exist
os.makedirs(sorted_media_directory, exist_ok=True)

# Define a function to sort a media file
def sort_media_file(filename):
    # Get the creation and modification dates of the file
    try:
        creation_date = datetime.fromtimestamp(os.path.getctime(filename))
        modification_date = datetime.fromtimestamp(os.path.getmtime(filename))
    except Exception as e:
        print(f'Error: {e} ({filename})')
        return

    # Use the oldest date as the date taken
    date_taken = min(creation_date, modification_date)

    # Create a new directory for the year and month if it doesn't exist
    year_month_directory = os.path.join(
        sorted_media_directory,
        str(date_taken.year),
        f"{date_taken.strftime('%m')}"
    )
    os.makedirs(year_month_directory, exist_ok=True)

    # Move the file to the sorted directory
    destination = os.path.join(year_month_directory, os.path.basename(filename))
    shutil.move(filename, destination)
    print(f"Moved '{filename}' to '{destination}'")

# Sort existing media files
for filename in get_media_files(root_directory):
    sort_media_file(filename)

# Define a function to sort new media files
def on_created(event):
    time.sleep(1)  # Wait for file to finish writing
    sort_media_file(event.src_path)

# Monitor the directory for new media files and sort them
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class MediaHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            on_created(event)

# Start the observer
observer = Observer()
observer.schedule(MediaHandler(), root_directory, recursive=True)
observer.start()

# Define a function to stop the observer
def stop_observer():
    observer.stop()
    observer.join()

# Define a function to create the taskbar icon and menu
try:
    import wx.adv

    class TaskBarIcon(wx.adv.TaskBarIcon):
        def __init__(self):
            super().__init__()
            icon = wx.Icon(wx.Bitmap('icon.ico'))
            self.SetIcon(icon, "Photo Sorter")

        def CreatePopupMenu(self):
            menu = wx.Menu()
            exit_item = menu.Append(wx.ID_EXIT, "Exit")
            self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
            return menu

        def on_exit(self, event):
            wx.CallAfter(self.Destroy)

    app = wx.App()
    tb = TaskBarIcon()
    app.MainLoop()

except Exception as e:
    print(f'Error: {e}')


while True:
    time.sleep(1)

