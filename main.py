import subprocess
import os
from clear_frames import clear_frames

clear_frames()
files = os.listdir("input")
first_file = files[0]
video_path = os.path.join("input", first_file)

subprocess.run([
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.2)'",
    "-vsync", "vfr",
              "-y",
    "frames/frame_%03d.jpg"
])