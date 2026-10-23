
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




# "a cute chibi anime character in a funny comedic pose or falling down"




'''
    flagged = []
    scores = {} '''

'''
    if is_candidate:
    flagged.append((path, image_features))  # !!!!  both the path and the 1D vector.  !!!!
    scores[path] = margin '''