import os
from extract_frames import extract_frames
from clear_frames import clear_frames


clear_frames()

files = os.listdir("input")
if not files:
    print("Error: No files found in input folder.")
    exit()

first_file = files[0]

video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".webm")

if not first_file.lower().endswith(video_extensions):
    print("Error: Input file is not a supported video.")
    exit()

video_path = os.path.join("input", first_file)


extract_frames(video_path)