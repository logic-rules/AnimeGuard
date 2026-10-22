import subprocess
import re
def extract_frames(video_path):


    x = [
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.08)',showinfo, scale=-2:480",
    "-fps_mode", "vfr",
              "-y",
    "frames/frame_%04d.jpg"

    ]


    result = subprocess.run(x, capture_output=True, text=True) # the "result" shall now be captured by us (in a test/string form) instead of going to the console...
    return result

def extract_timestamps(result):
    timestamps = re.findall(r"pts_time:([\d.]+)", result.stderr)  # timestamps for each extracted frame, "re" searches for the specified pattern in the "result"'s stderr stream
    return timestamps