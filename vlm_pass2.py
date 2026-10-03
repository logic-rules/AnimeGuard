import ollama
import time
MODEL = "gemma3:4b"
VERIFY_PROMPT = (
    'Examine this anime frame strictly for explicit fanservice or exposed skin. '
    'Reply YES ONLY IF you see: '
    '1. Exposed cleavage, bare stomach/midriff, or bare thighs/buttocks. '
    '2. Visible underwear, lingerie, skimpy bikinis, or an upskirt shot showing underwear. '
    '3. Characters actively kissing or in an intimate sexualized pose. '
    'Reply NO if the character is wearing standard fully-covering clothes, standard school uniforms, '
    'or loose long-sleeve pajamas with NO bare skin showing, regardless of body shape or camera angle. '
    'Reply strictly with ONLY YES or NO.'
)

def flag_vlm(frames):
    print(f"Loading {MODEL}...")
    flagged_vlm = []
    start = time.time()
    for count, frame in enumerate(frames, start=1):
        response = ollama.chat(
            model = MODEL,
            messages = [{
                'role': 'user',
                'content': VERIFY_PROMPT,
                'images': [frame],
            }],
            options = {'num_predict': 5, 'temperature': 0.0}
        )

        if "YES" in response['message']['content']:
            flagged_vlm.append(frame)
        tag = "🚩" if "YES" in response['message']['content'] else "safe"

        elapsed = time.time() - start
        avg = elapsed / count

        print(
            f"[{count}/{len(frames)}] {frame} | {tag} | flagged:"
            f" {len(flagged_vlm)} | ETA: {(len(frames) - count) * avg:.0f}s",
            flush=True,
        )

    print(f"\nDone in {time.time() - start:.1f}s.")
    print(f"{len(flagged_vlm)}/{len(frames)} flagged")


    return flagged_vlm