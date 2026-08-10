import subprocess
def extract_frames(video_path):

    subprocess.run([
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.2)'",
    "-vsync", "vfr",
              "-y",
    "frames/frame_%03d.jpg"
])