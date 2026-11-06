# Evaluation Script

Developer tool for measuring how well the detector (Pass 1/2/both) finds scenes. You don't need this to use AnimeGuard.

## Truth files

Put one file (.txt) per episode in `eval/truth/`, one scene/range per line. Example:

```
02:38-02:40 2
02:59-03:35 1
```

Format is `start-end level`, with times as `MM:SS`.

- **Level 1:** clear fanservice. Always counts.
- **Level 2:** borderline (leg crops, tight hugs, fashion poses). Counts only in STRICT.

## Run

1. Scan the episode with AnimeGuard to produce `output/flagged_ranges.json`.
2. Run:

```
python eval/score.py eval/truth/<episode>.txt output/flagged_ranges.json
```

## Output

- **Precision:** how many flagged ranges were correct.
- **Recall:** how many truth scenes were found.
- **False alarms / Missed:** the exact ranges.

A flagged range counts as a hit if it comes within 2 seconds of a truth range.

- **STRICT:** levels 1+2.
- **STANDARD:** level 1 only. Flags that land on level 2 scenes are ignored.

Full level definitions are in commit 731cc21.