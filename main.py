import os
from extract_frames import extract_frames
from clear_frames import clear_frames

clear_frames()

files = os.listdir("input")
first_file = files[0]
video_path = os.path.join("input", first_file)

extract_frames(video_path)