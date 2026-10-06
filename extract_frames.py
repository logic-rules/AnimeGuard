import subprocess

def extract_frames(video_path):

    
    x = [
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.08)', scale=-2:480",
    "-fps_mode", "vfr",
              "-y",
    "frames/frame_%04d.jpg" ]


    subprocess.run(x)