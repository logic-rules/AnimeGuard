import os
import shutil
import json
import time

import typer
from typing import Annotated

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.markup import escape

VERSION = "1.0.0"
console = Console()

from extract_frames import extract_frames # initial frame and timestamps extraction (ffmpeg) every run
from pathlib import Path
from reset_folder import reset_folder # reset the two frame-inhibiting folders every run
from group_ranges import group_ranges
from clip_pass1 import flag_clip, MARGIN_THRESHOLD, NUM_THREADS, EXTRA

GAP_SECONDS = 15 # for ranges func

def main(
    margin: Annotated[float, typer.Option(help="Score margin needed to flag a frame (lower = more flags)")] = MARGIN_THRESHOLD,
    video: Annotated[Path | None, typer.Option(exists=True, dir_okay=False, help="Path to video file (skips the input/ folder)")] = None,
    threads: Annotated[int, typer.Option(help="Number of threads to use")] = NUM_THREADS,
    gap: Annotated[int, typer.Option(help="Max seconds between flagged frames to merge into one range")] = GAP_SECONDS,
    extra: Annotated[bool, typer.Option("--extra", help="Print per-frame details, dedup summary, etc.")] = EXTRA,
):
    t0 = time.time()

    name = "A N I M E G U A R D"
    title = Text()
    # calculates a ratio from 0 (first letter) to 1 (last letter) to smoothly blend the colors across "name"
    for i, ch in enumerate(name):
        t = i / (len(name) - 1)
        title.append(ch, style=f"bold rgb({int(80 * t)},{int(255 - 135 * t)},255)") # red increases, green decreases, and blue stays maxed out. these 3 colors work together to shift "name" from cyan to purple.

    console.print() # new-line
    console.rule(characters="·", style="cyan")  # repeater (cute dotted line)
    console.print(Align.center(title))
    console.print(Align.center(f"[dim]v{VERSION}  ·  finds the fanservice so you can skip it[/dim]"))

    if margin != MARGIN_THRESHOLD and gap != GAP_SECONDS:
        console.print(Align.center(f"[cyan]margin:[/cyan] {margin}   [cyan]gap:[/cyan] {gap}s"))
    elif margin != MARGIN_THRESHOLD:
        console.print(Align.center(f"[cyan]margin:[/cyan] {margin}"))
    elif gap != GAP_SECONDS:
        console.print(Align.center(f"[cyan]gap:[/cyan] {gap}s"))
    console.rule(characters="·", style="cyan") # repeater (cute dotted line)
    console.print() # new-line

    # wipe and recreate
    reset_folder("frames")
    reset_folder("flagged")

    if video:
        ffile = video.name # name
        video_path = str(video) # full path
    else:
        os.makedirs("input", exist_ok=True) # automatically create... ONLY IF IT DOESN'T ALREADY EXIST!
        file = os.listdir("input")

        if not file:                  # i.e. if line 8... previous line is just NOT!
            console.print("[bold red]Error: No files found in input folder.[/bold red]")
            raise typer.Exit(1)
        if len(file) > 1:
            console.print("[bold red]Error: more than one file in input/. Keep only one episode.[/bold red]")
            raise typer.Exit(1)

        ffile = file[0]

        video_path = os.path.join("input", ffile)

    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".webm")
    if not ffile.lower().endswith(video_extensions):  # checks extensions (and lowercase handling at that too)
        console.print("[bold red]Error: Input file is not a supported video.[/bold red]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] [dim]Input: {escape(ffile)}[/dim]")

    timestamps = extract_frames(video_path)

    flagged_frames = sorted(flag_clip(timestamps, margin, threads, extra))

    # ---------------------------------------------------------------------

    tflog = []
    seconds_list = []

    for path in flagged_frames:
        shutil.copy(path, "flagged") # type: ignore     # (copies the list into the "flagged" dir)


        # TIMESTAMPS:
        frame = os.path.basename(path)   # type: ignore
        number = int(frame[6:10])
        org_sec = float(timestamps[number - 1])
        seconds_list.append(org_sec)

        minutes = int(org_sec // 60)
        secs = int(org_sec % 60)

        time_str = f"{minutes:02d}:{secs:02d}"
        tflog.append({"frame": frame, "time": time_str})

    with open("flagged.json", "w", encoding = "utf-8") as f:
        json.dump(tflog, f, indent = 2)


    # RANGES:
    ranges = group_ranges(seconds_list, gap) # function for converting timestamps into ranges

    range_log = []
    for start, end in ranges: # for creating (range_str)s
        range_str = f"{int(start // 60):02d}:{int(start % 60):02d}-{int((end + 1) // 60):02d}:{int((end + 1) % 60):02d}"
        range_log.append(range_str)

    with open("flagged_ranges.json", "w", encoding = "utf-8") as f:
        json.dump(range_log, f, indent = 2)

    if not range_log:
        console.print("[dim]No flagged ranges found.[/dim]")
    else:
        table = Table(title="\nFlagged Ranges", title_style="bold cyan", header_style="bold cyan")
        table.add_column("#", style="dim")
        table.add_column("Range", style="cyan")

        for count, r in enumerate(range_log, start = 1):
            table.add_row(str(count), r)

        console.print(table)

    elapsed = time.time() - t0
    console.print(
        f"\n[green]✓[/green] [dim]{len(timestamps)} frames scanned · "
        f"{len(flagged_frames)} flagged · {len(ranges)} ranges · "
        f"{int(elapsed // 60)}m {int(elapsed % 60):02d}s[/dim]"
    )


if __name__ == "__main__":
    typer.run(main)