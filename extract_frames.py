import subprocess
import re
from rich.console import Console
import typer
console = Console()

def extract_frames(video_path):


    x = [
    "ffmpeg", "-i", video_path,
    "-vf", "select='gt(scene,0.08)',showinfo, scale=-2:480",
    "-fps_mode", "vfr",
              "-y",
    "frames/frame_%04d.jpg"

    ]
    with console.status("[bold green]Extracting frames..."):
        try:
            result = subprocess.run(x, capture_output=True, text=True)  # the "result" shall now be captured by us (in a test/string form) instead of going to the console...
        except FileNotFoundError:
            console.print("[bold red]Error: ffmpeg not found. Install it and make sure it's on your PATH.[/bold red]")
            raise typer.Exit(1)

    timestamps = re.findall(r"pts_time:([\d.]+)", result.stderr)  # timestamps for each extracted frame, "re" searches for the specified pattern in the "result"'s stderr stream

    if result.returncode != 0 and not timestamps:
        console.print("[bold red]Error: ffmpeg could not read this video.[/bold red]")
        raise typer.Exit(1)

    console.print("[green]✓[/green] [dim]Frames extracted[/dim]")
    return timestamps