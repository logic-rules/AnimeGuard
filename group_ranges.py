def group_ranges(seconds_list, gap=30):
    if not seconds_list:
        return []
    ranges = []

    start = seconds_list[0]  # acts as anchored beginning point
    prev = seconds_list[0]  # acts as moving tracker to measure distance against next "s"

    for s in seconds_list[1:]:
        if s - prev > gap:  # checks gap
            # if above condition is true: range is saved, the anchored beginning point "start" is reset to the current "s", else (if gap is not enough), "start" stays the same.
            ranges.append((start, prev))
            start = s
        prev = s  # always updates to the latest "s" regardless of any condition
    ranges.append((start, prev))  # the final range, which the loop can't go through.

    return ranges