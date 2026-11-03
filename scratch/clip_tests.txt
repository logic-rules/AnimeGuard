
'''
    ranked = sorted(fullpath_flagged, key=lambda p: scores[p], reverse=True) # ranking mechanism which maybe useful later... (was foundation of today's testing, keeping for potential future use)
    top20 = sorted(ranked[:20])
    bottom20 = sorted(ranked[-20:]) '''


''' if frame_name in ("frame_0074.jpg", "frame_0226.jpg"):
    best_safe = ALL_LABELS[cosine_sims[:len(SAFE_LABELS)].argmax().item()] # type: ignore
    print("   WINNING SAFE LABEL:", best_safe) ''' # notes: this test is only for GENUINE FRAMES WHICH WERE NOT FLAGGED, not for false positives.
    # doesn't work on flagged frames, as their best_safe label is less than their best_sug label (cosine_sim), doesn't work on consecutive frames with the same best_safe label

''' if frame_name in ("frame_0257.jpg", "frame_0653.jpg", "frame_1140.jpg"):
    best_sug = SUGGESTIVE_LABELS[cosine_sims[len(SAFE_LABELS):].argmax().item()] # type: ignore
    print("   WINNING SUGGESTIVE LABEL:", best_sug) ''' # notes: this test is only for FALSE POSITIVES, not for genuine frames which were not flagged.
    # only works on flagged frames, as their best_sug label is more than their best_safe label (cosine_sim), doesn't work on consecutive frames with the same best_sug label
    #   ⬆️⬆️⬆️⬆️⬆️   REPLACE the "if" statement with "if is_candidate:" if testing on all flagged frames    ⬆️⬆️⬆️⬆️⬆️


# "a cute chibi anime character in a funny comedic pose or falling down"




'''
    flagged = []
    scores = {} '''

'''
    if is_candidate:
    flagged.append((path, image_features))  # !!!!  both the path and the 1D vector.  !!!!
    scores[path] = margin '''


'''
margin = max_suggestive_cos - max_safe_cos
        if frame_name == "frame_0620.jpg":
            best_safe = ALL_LABELS[cosine_sims[:len(SAFE_LABELS)].argmax().item()]  # type: ignore
            print("   WINNING SAFE LABEL:", best_safe)
            best_sug = SUGGESTIVE_LABELS[cosine_sims[len(SAFE_LABELS):].argmax().item()]  # type: ignore
            print("   WINNING SUGGESTIVE LABEL:", best_sug)
        is_candidate = (max_suggestive_cos >= dynamic_min_cos) and (margin >= dynamic_margin)
        if is_candidate:
            print(f" YOOO LOOK OVER HEREEEE  {frame_name}: sug_cos={max_suggestive_cos:.3f} "
            f"safe_cos={max_safe_cos:.3f} margin={margin:+.3f})")
        if is_candidate:
            flagged.append((path, image_features)) #  !!!!  both the path and the 1D vector.  !!!!
        elapsed = time.time() - start
        avg = elapsed / count
        tag = "🚩" if is_candidate else "safe"




    print(f"\nDone in {time.time() - start:.1f}s.")
    print(f"{len(flagged)}/{total} candidate frames BEFORE deduplication.")

    deduped = dedupe_flagged(flagged)

    display_flagged = [os.path.basename(path) for path, _ in deduped] # print
    print(f"{len(display_flagged)} candidate frames remaining AFTER deduplication.")
    print("Flagged files: ", display_flagged)

    fullpath_flagged = [path for path, _ in deduped]  # full path string





flag_clip() '''