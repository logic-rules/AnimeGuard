import os

def clear_frames():
    files = os.listdir("frames")
    for filename in files:
        full_path = os.path.join("frames", filename)
        os.remove(full_path)


def clear_flagged():
    files = os.listdir("flagged")
    for filename in files:
        full_path = os.path.join("flagged", filename)
        os.remove(full_path)