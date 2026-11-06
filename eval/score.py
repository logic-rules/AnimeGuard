import json
import sys

TOL = 2 # seconds buff


def to_seconds(time_str): # converts a timestamp "(xx:xx)" into simple seconds (int)
    parts = time_str.split(":") # "xx:xx" --> list of ("xx" "xx")
    if len(parts) == 3: # 3 parts, i.e. an hour
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

    elif len(parts) == 2: # 2 parts, i.e. a minute
        return int(parts[0]) * 60 + int(parts[1])

    return int(time_str) # already in simple seconds, (int)


def parse_range(text): # 1. range ("xx:xx-xx:xx") --> 2. list of ("xx" "xx" "xx" "xx') --> 3. first 2 ("xx" "xx") = "xx:xx", 4. same for next 2
    text = text.strip()
    if text.count("-") == 3: # edge case of 3 hyphens
        parts = text.split("-")
        start = f"{parts[0]}:{parts[1]}"
        end = f"{parts[2]}:{parts[3]}"
    else:
        start, end = text.rsplit("-", 1) # normal case, splits right to left into "start" and "end" using the one hyphen

    return to_seconds(start), to_seconds(end)


def fmt(r): # formatting display seconds values back into clean ranges ("xx:xx-xx:xx")
    return f"{r[0] // 60:02d}:{r[0] % 60:02d}-{r[1] // 60:02d}:{r[1] % 60:02d}"


def load_truth(path): # our custom ranges
    ranges = []
    with open(path, encoding="utf-8") as f:
        for line in f: # loops through each line (xx:xx-xx:xx) in the truth file, provided
            if not line.strip(): # skip line if it's NOT there. (tip: empty = False, non-empty = True)
                continue
            parts = line.split() # split by space, into list ("xx:xx-xx:xx", "1 (or) 2")
            level = int(parts[1]) if len(parts) > 1 else 1 # checks for the level. 1 or 2.
            ranges.append((parse_range(parts[0]), level)) # parse range function (above), a tuple ((xx,xx), x) (int)
    return ranges


def load_pred(path): # the flagged ranges
    with open(path, encoding="utf-8") as f:
        return [parse_range(r) for r in json.load(f)] # parse range function (above), a tuple ((xx,xx), (xx,xx)) (int)


def close(p, t):
    return p[0] <= t[1] + TOL and p[1] >= t[0] - TOL # 1. checks if prediction (p) starts BEFORE(<) or WHEN(=) the truth (t) ends (+2s buff), 2. checks if prediction (p) ends AFTER(>) or WHEN(=) the truth (t) starts (-2s buff). True when they "overlap or touch within 2s", else False.


def evaluate(pred_list, truth_list): # takes both lists and evaluates which of each match
    matched_preds, matched_truth = set(), set()

    for p_idx, p in enumerate(pred_list): # track index and value of each p
        for t_idx, t in enumerate(truth_list): # track index and value of each t
            if close(p, t):
                matched_preds.add(p_idx)
                matched_truth.add(t_idx)
    return matched_preds, matched_truth


pred = load_pred(sys.argv[2])
all_truth = load_truth(sys.argv[1])

for label, max_level in (("ALL/STRICT (levels 1+2)", 2), ("DEFINITE/RELAXED/STANDARD (level 1 only)", 1)): # label and level
    truth = [r for r, lvl in all_truth if lvl <= max_level] # keep those truths which are allowed by current max_level
    ignore = [r for r, lvl in all_truth if lvl > max_level]  # ignore those truths which are not allowed by current max_level

    matched_preds, matched_truth = evaluate(pred, truth)

    # checks if any unmatched p accidentally reached "ignore", to exclude it from being a false alarm in the final output
    ignored = {
        i for i, p in enumerate(pred)
        if i not in matched_preds and any(close(p, t) for t in ignore)
    }

    scored = len(pred) - len(ignored)
    genuine_count = len(matched_preds) # precision (when both --> truth, pred match)
    found_count = len(matched_truth) # recall


    print(f"\n{label}")
    print(f"  Precision: {genuine_count}/{scored} = {genuine_count / max(scored, 1):.0%}  (ignored {len(ignored)} flags on level 2 scenes)")
    print(f"  Recall:    {found_count}/{len(truth)} = {found_count / max(len(truth), 1):.0%}")
    print("  False alarms:", [fmt(pred[i]) for i in range(len(pred)) if i not in matched_preds and i not in ignored])
    print("  Missed:", [fmt(truth[i]) for i in range(len(truth)) if i not in matched_truth])