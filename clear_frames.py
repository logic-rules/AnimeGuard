import os

def clear_frames():
    files = os.listdir("frames")
    for filename in files:
        full_path = os.path.join("frames", filename)
        os.remove(full_path)