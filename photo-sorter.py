import os
import shutil
from datetime import datetime
import mimetypes

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
                media_files.append(os.path.join(root, filename))
    return media_files

# Define the root directory to sort through
root_directory = r"C:\Users\paris\OneDrive\Pictures\Camera Roll\Photos"

# Define the directory to store sorted media files
sorted_media_directory = os.path.join(root_directory, "Media")

# Create the directory if it doesn't exist
os.makedirs(sorted_media_directory, exist_ok=True)

# Loop through each media file in the directory and its subdirectories
for filename in get_media_files(root_directory):
    # Get the creation and modification dates of the file
    try:
        creation_date = datetime.fromtimestamp(os.path.getctime(filename))
        modification_date = datetime.fromtimestamp(os.path.getmtime(filename))
    except Exception as e:
        print(f'Error: {e} ({filename})')
        continue

    # Use the oldest date as the date taken
    date_taken = min(creation_date, modification_date)

    # Create a new directory for the year and month
    year_month_directory = os.path.join(
        sorted_media_directory,
        str(date_taken.year),
        f"{date_taken.strftime('%B')}"
    )
    os.makedirs(year_month_directory, exist_ok=True)

    # Copy the file to the sorted directory
    destination = os.path.join(year_month_directory, os.path.basename(filename))
    shutil.move(filename, destination)
    print(f"Moved '{filename}' to '{destination}'")
