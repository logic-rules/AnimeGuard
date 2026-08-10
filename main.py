import subprocess
import os
from clear_frames import clear_frames

clear_frames("frames")
files = os.listdir("input")
first_file = files[0]
video_path = os.path.join("input", first_file)

subprocess.run([
    "ffmpeg", "-i", video_path,
    "-vf", "fps=1",
    "-ss", "900", "-to", "950",
              "-y",
    "frames/frame_%03d.jpg"
])