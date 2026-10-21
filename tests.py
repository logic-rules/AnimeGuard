
'''
ranked = sorted(fullpath_flagged, key=lambda p: scores[p], reverse=True) # ranking mechanism which maybe useful later... (was foundation of today's testing, keeping for potential future use)
    top20 = sorted(ranked[:20])
    bottom20 = sorted(ranked[-20:]) '''


''' if frame_name in ("frame_0074.jpg", "frame_0226.jpg"):
    best_safe = ALL_LABELS[cosine_sims[:len(SAFE_LABELS)].argmax().item()] # type: ignore
    print("   WINNING SAFE LABEL:", best_safe) '''

# # "a cute chibi anime character in a funny comedic pose or falling down"

'''
flagged = []
scores = {} '''

'''
if is_candidate:
    flagged.append((path, image_features))  # !!!!  both the path and the 1D vector.  !!!!
    scores[path] = margin '''