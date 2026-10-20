import json
import os
import time
import ollama

MODEL = "qwen3-vl:4b-instruct"
DESCRIPTIONS_FILE = "descriptions.json"

DESCRIBE_PROMPT = (
    "Reply in exactly 3 sentences, with no introduction.\n"
    "Sentence 1: list each piece of clothing the character is wearing.\n"
    "Sentence 2: describe how much bare skin is visible and where, "
    "or say that none is visible.\n"
    "Sentence 3: their pose and what they are doing.\n"
    "State only what is visibly there. No feelings, mood, or interpretation."
)

JUDGE_PROMPT = (
    "You are a content filter for a conservative South Asian family.\n"
    "Below is a description of one anime frame. Reply YES if it describes any of: "
    "revealing clothing or swimwear, bare stomach/chest/thighs, underwear, "
    "a suggestive pose, a camera angle focused on a body, or romantic contact "
    "beyond hand-holding. Otherwise reply NO.\n"
    "Reply with only YES or NO.\n\n"
    "Description: "
)

frames = [
    'frames/frame_0044.jpg', 'frames/frame_0074.jpg', 'frames/frame_0076.jpg',
    'frames/frame_0095.jpg', 'frames/frame_0127.jpg', 'frames/frame_0146.jpg',
    'frames/frame_0181.jpg', 'frames/frame_0194.jpg', 'frames/frame_0198.jpg',
    'frames/frame_0201.jpg', 'frames/frame_0226.jpg', 'frames/frame_0227.jpg',
    'frames/frame_0228.jpg', 'frames/frame_0230.jpg', 'frames/frame_0235.jpg',
    'frames/frame_0255.jpg', 'frames/frame_0257.jpg', 'frames/frame_0260.jpg',
    'frames/frame_0268.jpg', 'frames/frame_0364.jpg', 'frames/frame_0430.jpg',
    'frames/frame_0432.jpg', 'frames/frame_0439.jpg', 'frames/frame_0512.jpg',
    'frames/frame_0523.jpg', 'frames/frame_0528.jpg', 'frames/frame_0534.jpg',
    'frames/frame_0548.jpg', 'frames/frame_0604.jpg', 'frames/frame_0618.jpg',
    'frames/frame_0629.jpg', 'frames/frame_0633.jpg', 'frames/frame_0635.jpg',
    'frames/frame_0638.jpg', 'frames/frame_0643.jpg', 'frames/frame_0646.jpg',
    'frames/frame_0651.jpg', 'frames/frame_0653.jpg', 'frames/frame_0662.jpg',
    'frames/frame_0667.jpg', 'frames/frame_0673.jpg', 'frames/frame_0686.jpg',
    'frames/frame_0694.jpg', 'frames/frame_0707.jpg', 'frames/frame_0714.jpg',
    'frames/frame_0727.jpg', 'frames/frame_0731.jpg', 'frames/frame_0750.jpg',
    'frames/frame_0806.jpg', 'frames/frame_0816.jpg', 'frames/frame_0819.jpg',
    'frames/frame_0820.jpg', 'frames/frame_0823.jpg', 'frames/frame_0826.jpg',
    'frames/frame_0836.jpg', 'frames/frame_0850.jpg', 'frames/frame_0851.jpg',
    'frames/frame_0895.jpg', 'frames/frame_0941.jpg', 'frames/frame_0945.jpg',
    'frames/frame_0952.jpg', 'frames/frame_0989.jpg', 'frames/frame_1032.jpg',
    'frames/frame_1052.jpg', 'frames/frame_1085.jpg', 'frames/frame_1112.jpg',
    'frames/frame_1113.jpg', 'frames/frame_1116.jpg', 'frames/frame_1128.jpg',
    'frames/frame_1140.jpg', 'frames/frame_1148.jpg', 'frames/frame_1150.jpg',
    'frames/frame_1160.jpg', 'frames/frame_1171.jpg', 'frames/frame_1173.jpg'
]


def describe_all():
    descriptions = {}
    if os.path.exists(DESCRIPTIONS_FILE):
        with open(DESCRIPTIONS_FILE) as f:
            descriptions = json.load(f)

    for count, frame in enumerate(frames, start=1):
        if descriptions.get(frame):
            continue
        frame_start = time.time()
        response = ollama.chat(
            model=MODEL,
            messages=[{'role': 'user', 'content': DESCRIBE_PROMPT, 'images': [frame]}],
            keep_alive='10m',
            options={'num_predict': 80, 'temperature': 0.0, 'num_thread': 6},
        )
        descriptions[frame] = response['message']['content'].strip()
        with open(DESCRIPTIONS_FILE, "w") as f:
            json.dump(descriptions, f, indent=2)
        print(f"[{count}/{len(frames)}] {frame} ({time.time() - frame_start:.1f}s)", flush=True)
        print("    ", descriptions[frame], flush=True)
    return descriptions


def judge_all(descriptions):
    flagged_vlm = []
    for count, frame in enumerate(frames, start=1):
        description = descriptions[frame]
        response = ollama.chat(
            model=MODEL,
            messages=[{'role': 'user', 'content': JUDGE_PROMPT + description}],
            keep_alive='10m',
            options={'num_predict': 3, 'temperature': 0.0, 'num_thread': 6},
        )
        is_flagged = "YES" in response['message']['content'].strip().upper()
        if is_flagged:
            flagged_vlm.append(frame)
        tag = "🚩" if is_flagged else "safe"
        print(f"[{count}/{len(frames)}] {frame} | {tag}\n    {description}\n", flush=True)
    print(f"{len(flagged_vlm)}/{len(frames)} flagged")
    return flagged_vlm


descriptions = describe_all()
flagged_vlm = judge_all(descriptions)



'''
import json
import re
import ollama

VISION_MODEL = "gemma3:4b"

JSON_PROMPT = """Analyze this anime frame carefully and return ONLY a raw JSON object with no markdown, no backticks, and no explanation.

Template:
{
  "head_or_face_present_in_frame": true or false,
  "crop_focus": "none" OR "legs_thighs" OR "chest" OR "torso",
  "exposed_skin": "none" OR "midriff" OR "swimwear",
  "clothing_description": "short description of clothing"
}

CRITICAL RULES:
- If you see a character in a standard room, dialogue scene, or upper-body shot, "head_or_face_present_in_frame" MUST be true and "crop_focus" MUST be "none".
- ONLY set "crop_focus" to "legs_thighs" if the camera is intentionally and tightly zoomed in on the lower legs/feet with the head entirely cut off.
- Standard characters wearing everyday clothes, aprons, or uniforms are NEVER a violation ("crop_focus": "none")."""
FRAMES = [
    'frames/frame_0044.jpg', 'frames/frame_0074.jpg', 'frames/frame_0076.jpg',
    'frames/frame_0095.jpg', 'frames/frame_0127.jpg', 'frames/frame_0146.jpg',
    'frames/frame_0181.jpg', 'frames/frame_0194.jpg', 'frames/frame_0198.jpg',
    'frames/frame_0201.jpg', 'frames/frame_0226.jpg', 'frames/frame_0227.jpg',
    'frames/frame_0228.jpg', 'frames/frame_0230.jpg', 'frames/frame_0235.jpg',
    'frames/frame_0255.jpg', 'frames/frame_0257.jpg', 'frames/frame_0260.jpg',
    'frames/frame_0268.jpg', 'frames/frame_0364.jpg', 'frames/frame_0430.jpg',
    'frames/frame_0432.jpg', 'frames/frame_0439.jpg', 'frames/frame_0512.jpg',
    'frames/frame_0523.jpg', 'frames/frame_0528.jpg', 'frames/frame_0534.jpg',
    'frames/frame_0548.jpg', 'frames/frame_0604.jpg', 'frames/frame_0618.jpg',
    'frames/frame_0629.jpg', 'frames/frame_0633.jpg', 'frames/frame_0635.jpg',
    'frames/frame_0638.jpg', 'frames/frame_0643.jpg', 'frames/frame_0646.jpg',
    'frames/frame_0651.jpg', 'frames/frame_0653.jpg', 'frames/frame_0662.jpg',
    'frames/frame_0667.jpg', 'frames/frame_0673.jpg', 'frames/frame_0686.jpg',
    'frames/frame_0694.jpg', 'frames/frame_0707.jpg', 'frames/frame_0714.jpg',
    'frames/frame_0727.jpg', 'frames/frame_0731.jpg', 'frames/frame_0750.jpg',
    'frames/frame_0806.jpg', 'frames/frame_0816.jpg', 'frames/frame_0819.jpg',
    'frames/frame_0820.jpg', 'frames/frame_0823.jpg', 'frames/frame_0826.jpg',
    'frames/frame_0836.jpg', 'frames/frame_0850.jpg', 'frames/frame_0851.jpg',
    'frames/frame_0895.jpg', 'frames/frame_0941.jpg', 'frames/frame_0945.jpg',
    'frames/frame_0952.jpg', 'frames/frame_0989.jpg', 'frames/frame_1032.jpg',
    'frames/frame_1052.jpg', 'frames/frame_1085.jpg', 'frames/frame_1112.jpg',
    'frames/frame_1113.jpg', 'frames/frame_1116.jpg', 'frames/frame_1128.jpg',
    'frames/frame_1140.jpg', 'frames/frame_1148.jpg', 'frames/frame_1150.jpg',
]


def clean_json_string(text: str) -> str:
    """Strip markdown backticks or stray wrapper text around JSON."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text


print(f"{'FRAME':<25} | {'VERDICT':<10} | {'REASON / DETAILS'}")
print("-" * 80)

for frame in FRAMES:
    try:
        res = ollama.chat(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": JSON_PROMPT, "images": [frame]}],
            options={"num_predict": 90, "temperature": 0.0, "num_thread": 6},
            format="json",
        )

        raw_content = res["message"]["content"].strip()
        cleaned_json = clean_json_string(raw_content)
        data = json.loads(cleaned_json)

        # Parse output with safe fallbacks
        face_present = data.get("head_or_face_present_in_frame", True)
        crop_focus = str(data.get("crop_focus", "none")).lower().strip()
        exposed_skin = str(data.get("exposed_skin", "none")).lower().strip()
        clothing_desc = str(data.get("clothing_description", "")).lower().strip()

        full_context = f"{crop_focus} {exposed_skin} {clothing_desc}"

        # -------------------------------------------------------------------
        # Precise Guardrail Logic
        # -------------------------------------------------------------------
        SAFE_KEYWORDS = ["apron", "pants", "trousers", "jacket", "coat", "full uniform"]

        if not face_present and crop_focus in ["legs_thighs", "chest", "torso"]:
            # CRITICAL: Never override a legs/thighs target violation crop
            if crop_focus == "legs_thighs":
                verdict = "YES"
                reason = f"No face + target crop on {crop_focus}"
            # Allow safe clothing overrides for torso/chest shots
            elif any(word in full_context for word in SAFE_KEYWORDS):
                verdict = "NO"
                reason = f"Covered attire override ({clothing_desc})"
            else:
                verdict = "YES"
                reason = f"No face + crop on {crop_focus}"

        elif exposed_skin in ["midriff", "swimwear"]:
            verdict = "YES"
            reason = f"Exposed skin: {exposed_skin}"

        else:
            verdict = "NO"
            reason = "Safe framing/attire"

        print(f"{frame:<25} | {verdict:<10} | {reason}")

    except Exception as e:
        print(f"{frame:<25} | ERROR      | {e}")

'''

