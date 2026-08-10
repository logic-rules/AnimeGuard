import os
from extract_frames import extract_frames # frame extraction
from clear_frames import clear_frames # frame clearance


clear_frames()

files = os.listdir("input")
if not files:                  # i.e. if line 8... previous line is just NOT!
    print("Error: No files found in input folder.")
    exit()

first_file = files[0]     # (we want just ONE SINGLE FILE per once to proceed)

video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".webm")

if not first_file.lower().endswith(video_extensions): # checks extensions (and lowercase handling at that too)
    print("Error: Input file is not a supported video.")
    exit()

video_path = os.path.join("input", first_file)


extract_frames(video_path)