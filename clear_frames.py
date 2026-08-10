import os

def clear_frames(folder):
    files = os.listdir(folder)
    for filename in files:
        full_path = os.path.join(folder, filename)
        os.remove(full_path)