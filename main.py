import os
import shutil
import json
from extract_frames import extract_frames # initial frame and timestamps extraction (ffmpeg) every run
from reset_folder import reset_folder # reset the two frame-inhibiting folders every run
from group_ranges import group_ranges
from clip_pass1 import flag_clip
from rich.console import Console
from rich.table import Table

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

flagged_frames = sorted(flag_clip(timestamps))

# -------------------------------------

tflog = []
seconds_list = []

for path in flagged_frames:
    shutil.copy(path, "flagged") # type: ignore     # (copies the list into the "flagged" dir)


    # TIMESTAMPS:
    frame = os.path.basename(path)   # type: ignore
    number = int(frame[6:10])
    org_sec = float(timestamps[number - 1])
    seconds_list.append(org_sec)

    minutes = int(org_sec // 60)
    secs = int(org_sec % 60)

    time_str = f"{minutes:02d}:{secs:02d}"
    tflog.append({"frame": frame, "time": time_str})

with open("flagged.json", "w", encoding = "utf-8") as f:
    json.dump(tflog, f, indent = 2)


# RANGES:
GAP_SECONDS = 15
ranges = group_ranges(seconds_list, GAP_SECONDS) # function for converting timestamps into ranges

range_log = []
for start, end in ranges: # for creating (range_str)s
    range_str = f"{int(start // 60):02d}:{int(start % 60):02d}-{int(end // 60):02d}:{int((end + 1) % 60):02d}"
    range_log.append(range_str)

with open("flagged_ranges.json", "w", encoding = "utf-8") as f:
    json.dump(range_log, f, indent = 2)

console = Console()
if not range_log:
    console.print("No flagged ranges found.")
else:
    table = Table(title="\nFlagged Ranges", title_style="bold red", header_style="bold cyan")
    table.add_column("#", style="dim")
    table.add_column("Range", style="yellow")

    for count, r in enumerate(range_log, start = 1):
        table.add_row(str(count), r)

    console.print(table)

console.print("\n[green]Done![/green]")