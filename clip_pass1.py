import glob
import os
import time
import numpy as np
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

FRAMES_FOLDER = "frames"

SAFE_LABELS = [
    "an anime character's face in close-up during dialogue",
    "an anime character fully clothed in casual daily wear",
    "an anime character in a standard school uniform",
    "an anime character in winter coat or formal jacket",
    "an anime action scene with motion blur or fighting effects",
    "an anime background landscape or scenery with no characters",
    "an anime character sitting or standing normally in a room",
    "a crowd or group of anime characters standing together",
    "an anime character crying or showing intense facial emotion",
    "an anime character with long hair",
    "an anime character wearing a standard fully-covered t-shirt or hoodie",
    "dramatic lighting, shadows, or color highlights on clothing",
    "a green male demon or monster with horns, armor, or holding a sword",
    "a male anime character with black feathered demon or angel wings",
    "an anime scene with heavy fog, mist, dark blue haze, or desaturated lighting",
    "a male anime character with bare shoulders or a shirtless male torso",
    "anime characters seen from behind a glass window, back view",
    "an anime demon lord or a muscular monster with horns",
    "anime characters leaning in talking, over the shoulder view",
    "an anime character lying sideways or his head collapsed on the ground",
    "heavily blurred image, censor blur, out of focus frame",

]

SUGGESTIVE_LABELS = [
    "a female anime character wearing an explicit bikini or swimsuit at a pool",
    "a female anime character in bare underwear, bra, or lingerie",
    "a shot focused directly on female exposed chest cleavage",
    "a female anime character with fully exposed bare stomach skin and midriff",
    "an upskirt camera angle explicitly showing female underwear under a skirt",
    "an anime character in an explicitly sexual pose",
    "a female anime character with an exaggerated bare chest emphasized by the camera",
    "two anime characters kissing on the lips in a romantic scene",
    "two anime characters lying together in an intimate romantic embrace",
    "a female anime character in revealing nightwear or sheer sleepwear",
    "a female anime character wearing an explicit attire designed to expose chest cleavage",
]

ALL_LABELS = SAFE_LABELS + SUGGESTIVE_LABELS

def get_image_entropy(img):
    gray_image = np.array(img.convert("L"))
    hist, _ = np.histogram(gray_image, bins=256, range=(0, 256))
    hist_norm = hist / hist.sum()
    hist_norm = hist_norm[hist_norm > 0]
    return -np.sum(hist_norm * np.log2(hist_norm))  # the formula for getting image entropy

print("Loading CLIP...")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
print("CLIP loaded.\n")

# precomputing text embeddings once
print(f"Pre-computing text embeddings for {len(ALL_LABELS)} labels...")
text_inputs = clip_processor(text=ALL_LABELS, return_tensors="pt", padding=True) # ts a dict consisting of input ids n stuff

with torch.inference_mode():
    # pass through text model then project to latent space
    text_outputs = clip_model.text_model(**text_inputs) # a whole ahh custom object
    pooled_text = text_outputs.pooler_output # a hidden part of that custom object, a tensor (2D) by itself, made of many summary vectors (1D tensors), one summary vector per label
    text_embeds = clip_model.text_projection(pooled_text) # turns the ([no. of labels],768) shape into ([no. of labels],512) to be able to put in latent comparable space of labels-image comparison
    # shape: (51, 512)
    text_features = text_embeds / text_embeds.norm(dim=-1, keepdim=True) # removes the raw size (magnitude) and only allow what is needed (direction/meaning, nothing else)

print("Text embeddings cached successfully.\n")

frames = sorted(glob.glob(f"{FRAMES_FOLDER}/*.jpg")) # find and sort
total = len(frames)
print(f"Total frames: {total}")

BASE_ABS_THRESHOLD = 0.40
MARGIN_THRESHOLD = 0.12

flagged = []
start = time.time() # timestamp captured once, right before the loop begins


for count, path in enumerate(frames, start=1): # a normal loop, but with an automatic counter (i.e. 2 vars instead of js 1)
    frame_name = os.path.basename(path) # to print the raw file name instead of the full path (at 2 places)
    image = Image.open(path).convert("RGB") # "method chaining" 1 --> open and decode image file. 2 --> converts to RGB color mode. i.e. two instances. 1st temp, 2nd perm. Only the second instance is stored in 'image'

    entropy = get_image_entropy(image)
    dynamic_abs_thresh = BASE_ABS_THRESHOLD + (0.08 if entropy < 5.2 else 0.0)

    image_inputs = clip_processor(images=image, return_tensors="pt")

    with torch.inference_mode():
        # pass through vision model then project to latent space
        image_outputs = clip_model.vision_model(**image_inputs)
        pooled_image = image_outputs.pooler_output
        image_embeds = clip_model.visual_projection(pooled_image)
        # shape: (1, 512)
        image_features = image_embeds / image_embeds.norm(dim=-1, keepdim=True)



        logit_scale = clip_model.logit_scale.exp() # blind worship fr
        logits_per_image = logit_scale * (image_features @ text_features.t()) # matmul: (1, 512) @ (512, 51) -> (1, 51)t
        probs = logits_per_image.softmax(dim=-1)[0] # before this line: raw scores. After this line: actual probabilities

    max_suggestive = probs[len(SAFE_LABELS) :].max().item()
    max_safe = probs[: len(SAFE_LABELS)].max().item()

    is_candidate = (max_suggestive > dynamic_abs_thresh) and (
        (max_suggestive - max_safe) > MARGIN_THRESHOLD
    )

    if is_candidate:
        flagged.append(frame_name)

    elapsed = time.time() - start
    avg = elapsed / count
    tag = "🚩" if is_candidate else "safe"

    print(
        f"[{count}/{total}] {frame_name}: sug={max_suggestive:.2f}"
        f" safe={max_safe:.2f} (ent={entropy:.1f}) {tag} | flagged:"
        f" {len(flagged)} | ETA: {(total - count) * avg:.0f}s",
        flush=True,
    )


print(f"\nDone in {time.time() - start:.1f}s.") # used 3 times in the whole script. check it out!
print(f"{len(flagged)}/{total} flagged as candidates.")
print("Flagged files:", flagged)