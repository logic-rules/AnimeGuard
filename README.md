# AnimeGuard

<p align="left">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-v3.12+-1f6feb?style=flat&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://github.com/openai/CLIP">
    <img src="https://img.shields.io/badge/vision-CLIP-238636?style=flat" alt="CLIP">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-8b949e?style=flat" alt="License">
  </a>
</p>

A local tool that scans an anime episode and flags scenes that look suggestive (or fanservice-y), with timestamps.

It was built for people who want to know where _such scenes_ are before watching, for example with family, so they can skip them.

<br>

<table align="center">
  <tr><th align="left">🔴 🟡 🟢 &nbsp; animeguard-demo.gif</th></tr>
  <tr><td><img src="animeguard-demo.gif" alt="AnimeGuard demo" width="550"></td></tr>
</table>

<br>

> **AnimeGuard is currently a rough first-pass filter, not an exact detector.** It favors showing you a bit too much over missing a scene, so treat the output as a short list to skim, not as a final answer.

## Table of Contents

- [How it works](#how-it-works)
- [Accuracy](#accuracy)
- [Known Limitations & Technical Trade-offs](#known-limitations--technical-trade-offs)
- [Installation](#installation)
  - [1. Install ffmpeg](#1-install-ffmpeg)
  - [2. Get the code](#2-get-the-code)
  - [3. Create and activate a virtual environment](#3-create-and-activate-a-virtual-environment)
  - [4. Install the packages](#4-install-the-packages)
  - [5. First run](#5-first-run)
- [Usage](#usage)
  - [Option A: the input/ folder](#option-a-the-input-folder)
  - [Option B: point at a file with --video](#option-b-point-at-a-file-with---video)
- [Options](#options)
- [Tested and rejected](#tested-and-rejected)
- [Roadmap](#roadmap)
- [License](#license)

## How it works

1. **Extract frames.** ffmpeg extracts one frame at each scene change, plus at least one every 2 seconds so slow shots aren't skipped, scaled down to 480px.
2. **Score with CLIP + a trained classifier.** A local CLIP model turns each frame into an embedding. A small classifier (logistic regression, trained on 10 hand-labeled episodes from 10 different shows) scores each embedding, and a frame is flagged when its score passes the cutoff (`0.7` by default, `0.85` with `--strict`).
3. **Save results.** Flagged frames are copied to `output/flagged/`, their timestamps written to `output/flagged.json`, and the ones close together by a specified gap are grouped into time ranges in `output/flagged_ranges.json`.

## Accuracy

Tested against scenes I labeled by hand. **Precision** is how many flagged ranges were real scenes, and **recall** is how many of the real scenes were found.

| | Precision | Recall |
|---|---|---|
| **10 training shows (each one held out while testing)** | | |
| Original CLIP-only rule | 50% | 82% |
| Classifier, default | 60% | 82% |
| Classifier, `--strict` | 86% | 50% |
| **3 shows it never saw** | | |
| Original CLIP-only rule | 50% | 56% |
| Classifier, default | 53% | 60% |
| Classifier, `--strict` | 80% | 23% |

- On the training shows, the classifier gives fewer false alarms at the same recall. On unseen shows the improvement is small.
- `--strict` gives a short, mostly correct list but misses a lot. Use it when you only want the clearest scenes.
- The labels are one person's opinion. Borderline scenes count, including shots where an exaggerated figure is drawn prominently, even without special framing or camera focus. The 3-show blind-test is also small, so treat those numbers as rough.

## Known Limitations & Technical Trade-offs

- **Expect false alarms.** AnimeGuard is tuned for **high recall over high precision**, meaning it throws plenty of false flags just to make sure it doesn't miss anything. Expect some (or more) flagged frames that are actually fine. In my tests, roughly 50-60% of flagged ranges were genuine at the default setting, depending on the episode (`--strict` raises this to about 80%, but misses more scenes). Ranges only a second or two long are more likely to be false-positives.
- **Missed scenes happen.** Missed scenes are possible, even with the best recall optimizations. On shows the classifier had never seen, the default setting found about 60% of the scenes I had labeled, and `--strict` far fewer, so don't treat the output as a complete list. Some stubborn, edge cases will slip through.
- **Weaker on wide shots.** Visual features get harder to pick up in distant background shots by the CLIP model.
- **No sense of motion or context.** CLIP's core nature is that it evaluates single static frames in isolation. It doesn't know what happened before or after.
- **Visuals only.** No audio, dialogue, or subtitle analysis.
- **Startup delay.** PyTorch takes a few seconds to load into memory on startup, and processing a full episode takes a few minutes on CPU.

## Installation

You need Python 3.12+ and ffmpeg beforehand.

### 1. Install ffmpeg

- **Windows:** `winget install "FFmpeg (Essentials Build)"`, then close and reopen your terminal so it's on your PATH.
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

Check with `ffmpeg -version`.

### 2. Get the code

With git:

```
git clone https://github.com/logic-rules/AnimeGuard.git
cd AnimeGuard
```

Without git: download "Source code (zip)" from the [latest release](https://github.com/logic-rules/AnimeGuard/releases/latest), extract it, and open a terminal inside the extracted folder.

### 3. Create and activate a virtual environment

```
python -m venv .venv
```

Then activate it:

- **Windows:** `.venv\Scripts\activate`
- **macOS/Linux:** `source .venv/bin/activate`

Your prompt should now start with `(.venv)`. If it doesn't, the packages in the next step won't install in the right place.

> **Windows PowerShell:** if activating fails with "running scripts is disabled on this system", run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the same window and paste again. It only applies to that window.

### 4. Install the packages

```
pip install -r requirements.txt
mkdir input
```

This downloads PyTorch and a few other dependencies (a few hundred MB), so it can take a while on a slow connection.

### 5. First run

The first run downloads the CLIP model from Hugging Face, so you need internet once. After that, everything runs offline.

## Usage

### Option A: the `input/` folder

1. Put **one** episode file in the `input/` folder (`.mp4`, `.mkv`, `.avi`, `.mov` or `.webm`).
   **Copy it, don't move it.** On Windows, hold **Ctrl** while dragging.
   AnimeGuard never deletes anything in `input/`, but a simple drag can *move* your only copy there, so copying keeps the original safe.
2. Run:
   ```
   python main.py
   ```

If `input/` is empty or holds more than one file, the tool stops with a one-line message.  

### Option B: point at a file with `--video`
 
```
python main.py --video "C:\Videos\Episode 01.mkv"
```
 
The file is read directly from its path. It is never copied, moved or deleted. On Windows, put the path in double quotes if it contains spaces.

**Results** appear in the terminal as a table of time ranges, a one-line summary, and in:
   - `output/flagged/`: copies of the flagged frames
   - `output/flagged.json`: each flagged frame with its timestamp (`MM:SS`)
   - `output/flagged_ranges.json`: flagged frames merge into time ranges (`MM:SS-MM:SS`)

`frames/` and `output/flagged/` are wiped at the start of every run, so move anything you want to keep. `input/` is never touched.

**Note:**
The progress bar needs a real terminal (PowerShell, Terminal, etc.). In PyCharm's Run window the bar may not be present, but the results are the same.

## Options

| Flag           | Default | What it does                                                                                                                                                                                                                                    |
|----------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--strict`     | off     | Uses a stricter cutoff (`0.85` instead of `0.7`). Far fewer false alarms (about 80% of flagged ranges were genuine in my tests), but it finds fewer scenes, so expect more misses. Good when you only want a short list of the clearest scenes. |
| `--gap`        | `15`    | Flagged frames closer together than this many seconds are merged into one range.                                                                                                                                                                |
| `--video PATH` | none    | Scan a file by its path, skipping `input/`.                                                                                                                                                                                                     |
| `--threads`    | auto    | CPU threads used by CLIP. Leave it unset and PyTorch picks based on your CPU.                                                                                                                                                                   |
| `--extra`      | off     | Print per-frame details.                                                                                                                                                                                                                        |

Run `python main.py --help` for the same list.

## Tested and rejected

### VLM Pass 2

- The original plan was a fast, local tool with a vision-language model (VLM) as a Pass 2 to cut false alarms. I tested Qwen2.5-VL 32B, a fairly large open model.
- On 46 manually labeled ranges (21 real, 25 false alarms), it kept 17 of the 21 real ones (81%) and dropped 11 of the 25 false alarms (44%).
- My set targets were 90% and 50%. It didn't pass. A 0-10 score prompt did worse.
- So, as expected, smaller models that normal setups can run are unlikely to do better (and this one needs a GPU far beyond a typical setup).
- I didn't test cloud or paid models, since AnimeGuard is meant to be free and local.
- The test set may also have affected the result: it was small and labeled by one person, so treat the numbers as rough.

### Classifier tweaks

None of these helped. Scores are mean average precision (how well genuine frames are ranked above false alarms, higher = better).

- Smoothing the scores over 3 frames gave about the same precision and recall.
- Adding the original CLIP scores as extras scored 0.49, against 0.50 without them.
- More training shows stopped helping at about 10. On two unseen shows the score was 0.318 with 10 shows and 0.319 with 14.

<details>
<summary><h3>How AnimeGuard got here</h3></summary>

1. **Straight to a vision-language model.** The first and simplest idea was to send raw frames directly to a local VLM and let it judge. On my CPU-only laptop, the 4B models I tried (including gemma3:4b and qwen3-vl:4b) took about 50-80+ seconds per frame. And when I checked the accuracy by eye, they got clothing and bare skin wrong. Smaller models were slightly faster, but worse accuracy.
2. **CLIP margin rule.** Switched to CLIP, comparing each frame against sets of "suggestive" and "safe" text labels and flagging a frame only when the suggestive score wins by a margin. I first used show-specific labels from 1-2 shows, but then switched to generic labels. Adding extra safe labels by grouping false alarms into types cut the flagged frames from 76 (~10 genuine) to 27 (9 of those 10 kept) on one episode. I stopped adding safe labels because each one risked taking real frames with it (e.g. winged character labels, male character labels).
3. **Near-duplicate frame removal.** I added it, then removed it in v1.1.0 since the output is now ranges instead of individual frames.
4. **Trained embeddings classifier.** I expected it to be a second-stage filter after the CLIP margin rule, but it replaced the rule. On the shows it trained on (each held out in turn), precision went from 50% to 60% at the same recall. On shows it never saw, the gain was small (50% to 53% precision, 56% to 60% recall).
5. **Classifier tweaks.** Smoothing, adding the old CLIP scores as helping features, and more training shows. None of them helped (see above).
6. **VLM Pass.** Tested last, and rejected (see above).

</details>

## Roadmap

A middle cutoff between the default and `--strict` is planned.

## License

MIT. See [LICENSE](LICENSE).

---

*Planned and built while learning. AI helped by explaining concepts, suggesting approaches and giving code snippets. Claude helped draft this README.*
