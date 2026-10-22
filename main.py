import os
import shutil
from extract_frames import extract_frames # initial frame and timestamps extraction (ffmpeg) every run
from reset_folder import reset_folder # reset the two frame-inhibiting folders every run
from clip_pass1 import flag_clip

# wipe and recreate
reset_folder("frames")
reset_folder("flagged")

# automatically create... ONLY IF IT DOESN'T ALREADY EXIST!
os.makedirs("input", exist_ok=True)

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

timestamps = extract_frames(video_path)

flagged_frames = sorted(flag_clip())

for path in flagged_frames:
    shutil.copy(path, "flagged") # type: ignore     # (copies the list into the "flagged" dir)


    # TIMESTAMPS:
    frame = os.path.basename(path)   # type: ignore
    number = int(frame[6:10])
    org_sec = float(timestamps[number - 1])
    minutes = int(org_sec // 60)
    secs = int(org_sec % 60)
    print(f"{minutes:02d}:{secs:02d}")