import subprocess

def extract_frames(video_path):
    subprocess.run([
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.1)', scale=-2:480",
    "-vsync", "vfr",
              "-y",
    "frames/frame_%04d.jpg" ])                                   #turn ts subprocesses ([]) thing simpler too in some way