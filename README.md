# Anime-Guard

A local tool that scans an anime episode and flags scenes that look suggestive (or like fanservice), with timestamps.

It was built for people who want to know where the questionable scenes are before watching, for example with family, so they can skip them.

## How it works

1. **Extract frames.** ffmpeg extracts one frame at a scene change (not at fixed intervals), scaled down to 480px.
2. **Screen with CLIP (Pass 1).** Each frame is compared by a local CLIP model against two sets of text descriptions: suggestive ones and "safe" ones (faces, school uniforms, scenery, and so on). A frame is flagged when it matches a suggestive description clearly better than any safe one. Near-duplicate flagged frames are removed.
3. **Save results.** Flagged frames are copied to `flagged/`, their timestamps written to `flagged.json`, and the ones close together by a specified gap are grouped into time ranges in `flagged_ranges.json`.

## Known limits

- Since CLIP was never trained on such task, it leans toward false alarms. Expect some (or more) flagged frames that are actually fine.
- It is weaker on wide shots and on frames focused on male characters.
- It looks at single still frames, so it has no sense of motion/context.
- A timestamp marks where a shot starts, not how long the content lasts.
- Tuning the labels was tested on a handful of episodes. Any safe label you add can also "steal" a genuinely suggestive frame, so the labels are intentionally left as they are.
- A frame that sits just under the threshold can be missed. Lowering `MARGIN_THRESHOLD` (see Settings) catches more of these, at the cost of more false-positives.
- Visual only. Audio, dialogue and subtitles are not analyzed. (yet)

## Install

You need Python 3.12+ (developed on 3.14) and ffmpeg.

1. **Install ffmpeg.**
   - Windows: `winget install "FFmpeg (Essentials Build)"`, then close and reopen your terminal so it's on your PATH.
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

   Check it with `ffmpeg -version`.
2. **Get the code and install the packages:**
   ```
   git clone https://github.com/logic-rules/AnimeGuard.git
   cd AnimeGuard
   python -m venv .venv
   ```
   Activate the virtual environment (Windows: `.venv\Scripts\activate`, macOS/Linux: `source .venv/bin/activate`), then:
   ```
   pip install -r requirements.txt
   mkdir input
   ```
   After the `activate` line, your prompt should start with `(.venv)`. If it doesn't, the packages won't install in the right place.
   On macOS/Linux, use `source .venv/bin/activate` instead of `.venv\Scripts\activate`.
   The installation downloads torch, which is a large download.
3. The first run downloads the CLIP model from Hugging Face, so you need internet once. After that, everything runs offline.

## Usage

1. Put **one** episode file in the `input/` folder (`.mp4`, `.mkv`, `.avi`, `.mov` or `.webm`).
   **Copy it, don't move it.** On Windows, hold **Ctrl** while dragging.
   Anime-Guard never deletes anything in `input/`, but a plain drag can *move* your only copy there, so copying keeps the original safe.
2. Run:
   ```
   python main.py
   ```
3. Results appear in:
   - `flagged/`: copies of the flagged frames
   - `flagged.json`: one entry per flagged frame, with its timestamp
   - `flagged_ranges.json`: nearby flags grouped into time ranges

`frames/` and `flagged/` are wiped at the start of every run, so move anything you want to keep. `input/` is never touched.

## Settings

- `MARGIN_THRESHOLD` (default `0.03`, top of `clip_pass1.py`): how strongly a frame must lean suggestive to be flagged. Lower it (for example `0.015`) to catch borderline frames, but expect more false alarms.
- `GAP_SECONDS` (default `15`, in `main.py`): flagged frames closer together than this are merged into one range.

### License

MIT. See [LICENSE](LICENSE).

---

*Planned and built while learning. Claude and Gemini helped by explaining concepts, suggesting approaches and giving code snippets. Claude also helped draft this README.*