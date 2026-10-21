import os
import shutil
from extract_frames import extract_frames # frame extraction
from clear_dir import clear_frames, clear_flagged
from clip_pass1 import flag_clip

clear_frames()
clear_flagged()

files = os.listdir("input")
if not files:                  # i.e. if line 8... previous line is just NOT!
    print("Error: No files found in input folder.")
    exit() # MANDATORY FOR IF THERES NO INPUT IN input
print("All files in input:", files)

first_file = files[0]     # (we want just ONE SINGLE FILE per once to proceed)

video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".webm")

if not first_file.lower().endswith(video_extensions): # checks extensions (and lowercase handling at that too)
    print("Error: Input file is not a supported video.")
    exit()

print("First file:", first_file)
video_path = os.path.join("input", first_file)

extract_frames(video_path)

flagged_frames = sorted(flag_clip())

for path in flagged_frames:
    shutil.copy(path, "flagged") # type: ignore