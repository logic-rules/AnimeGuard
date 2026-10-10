import glob
import os
import time
import numpy as np
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

# minimum cosine similarity for a frame to be considered a suggestive prompt
MIN_SUGGESTIVE_COSINE = 0.25

# minimum suggestive score OVER the top safe score
MARGIN_THRESHOLD = 0.03

DEDUPE_SIMILARITY_THRESHOLD = 0.93 # dedup

NUM_THREADS = 10
torch.set_num_threads(NUM_THREADS) # custom thread count for multicore CPU


SAFE_LABELS = [
    # character & everyday attire
    "an anime character's face or headshot talking",
    "an anime character in school uniform, jacket, hoodie, sweater, or winter coat",
    "a group of fully clothed anime characters standing or sitting together",
    "an anime character walking, running, sitting, or eating normally",

    # specific Backgrounds & scene props
    "white plastic garbage bags, trash cans, or a green protective mesh net",
    "a birdcage, cloth cover, hanging curtain, or lamp shade",
    "abstract colorful circles, dots, patterns, geometry, or anime title graphics",
    "an empty anime school hallway, classroom, windows, or building corridor",
    "anime scenery, landscape, street, trees, blue sky, or clouds",
    "household furniture, table, desk, chair, room walls, or floor",
    "a close-up shot of small inanimate objects, books, or papers"
]

SUGGESTIVE_LABELS = [
    # Directly exposed & swimwear
    "a female anime character wearing a swimsuit, bikini, or swimsuit top",
    "a female anime character in bare underwear, bra, or panties",

    # partial skin exposure
    "a female anime character with exposed bare cleavage or bare breasts",
    "a female anime character with bare exposed stomach, navel, or midriff",
    "a female anime character with bare exposed thighs, buttocks, or hip skin",

    # angles & poses
    "a close-up shot looking up under an anime short skirt or dress",
    "an intimate sexualized anime pose or provocative bed scene"
]

ALL_LABELS = SAFE_LABELS + SUGGESTIVE_LABELS


def get_image_entropy(image):
    gray_image = np.array(image.convert("L"))
    hist, _ = np.histogram(gray_image, bins=256, range=(0, 256))
    hist_norm = hist / hist.sum()
    hist_norm = hist_norm[hist_norm > 0]
    return -np.sum(hist_norm * np.log2(hist_norm))  # the formula for getting image entropy


def dedupe_flagged(flagged): # used later for deduplication
    deduped = []
    for path, features in flagged: # for each. (a reminder uh nvm)
        if deduped: # checks if empty or not. skips for first frame.
            prev_path, prev_features = deduped[-1]
            similarity = (features @ prev_features.t()).item()
            if similarity > DEDUPE_SIMILARITY_THRESHOLD:
                continue # if above line is true, it doesn't append the frame, i.e, removing it. mission accomplished.
        deduped.append((path, features))
    return deduped


def flag_clip():
    print("Loading CLIP...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    clip_model.eval()
    print("CLIP loaded.\n")

    # precomputing text embeddings once
    print(f"Pre-computing text embeddings for {len(ALL_LABELS)} labels...")
    text_inputs = clip_processor(text=ALL_LABELS, return_tensors="pt", padding=True)

    with torch.inference_mode():
        # pass through text model then project to latent space
        text_outputs = clip_model.text_model(**text_inputs) # a whole ahh custom object
        pooled_text = text_outputs.pooler_output # a hidden part of that custom object, a tensor (2D) by itself, made of many summary vectors (1D tensors), one summary vector per label
        text_embeds = clip_model.text_projection(pooled_text) # turns the ([no. of labels],768) shape into ([no. of labels],512) to be able to put in latent comparable space of labels-image comparison
        # shape: (xx,512)
        text_features = text_embeds / text_embeds.norm(dim=-1, keepdim=True) # removes the raw size (magnitude) and only allow what is needed (direction/meaning, nothing else)

    print("Text embeddings cached successfully.\n")
    frames = sorted(glob.glob("frames/*.jpg")) # find n sort
    total = len(frames)
    print(f"Total frames: {total}")

    flagged = []
    start = time.time() # timestamp captured once, right before the loop begins

    for count, path in enumerate(frames, start=1):  # a normal loop, but with an automatic counter (i.e. 2 vars instead of js 1)
        frame_name = os.path.basename(path) # to print the raw file name instead of the full path (at 2 places)
        image = Image.open(path).convert("RGB") # "method chaining" 1 --> open and decode image file. 2 --> converts to RGB color mode. i.e. two instances. 1st temp, 2nd perm. Only the second instance is stored in 'image'

        entropy = get_image_entropy(image)
        dynamic_min_cos = MIN_SUGGESTIVE_COSINE + (0.010 if entropy < 5.0 else 0.0)
        dynamic_margin = MARGIN_THRESHOLD + (0.005 if entropy < 5.0 else 0.0)

        image_inputs = clip_processor(images=image, return_tensors="pt")

        with torch.inference_mode():
            # pass through vision model then project to latent space
            image_outputs = clip_model.vision_model(**image_inputs)
            pooled_image = image_outputs.pooler_output
            image_embeds = clip_model.visual_projection(pooled_image)
            # shape: (1, 512)
            image_features = image_embeds / image_embeds.norm(dim=-1, keepdim=True)


            # Cosine similarity matmul
            cosine_sims = (image_features @ text_features.t())[0]

        max_suggestive_cos = cosine_sims[len(SAFE_LABELS):].max().item()
        max_safe_cos = cosine_sims[: len(SAFE_LABELS)].max().item()

        margin = max_suggestive_cos - max_safe_cos

        is_candidate = (max_suggestive_cos >= dynamic_min_cos) and (margin >= dynamic_margin)

        if is_candidate:
            flagged.append((path, image_features)) #  !!!!  both the path n the 1D vector.  !!!!

        elapsed = time.time() - start
        avg = elapsed / count
        tag = "🚩" if is_candidate else "safe"

        print(
            f"[{count}/{total}] {frame_name}: sug_cos={max_suggestive_cos:.2f} "
            f"safe_cos={max_safe_cos:.2f} margin={margin:+.3f} (ent={entropy:.1f}) {tag} | "
            f"flagged: {len(flagged)} | ETA: {(total - count) * avg:.0f}s",
            flush=True,
        )

    print(f"\nDone in {time.time() - start:.1f}s.")
    print(f"{len(flagged)}/{total} candidate frames BEFORE deduplication.")

    deduped = dedupe_flagged(flagged)
    fullpath_flagged_after_dedup = [path for path, _ in deduped] # we need full path string for tier 2

    display_flagged_after_dedup = [os.path.basename(path) for path, _ in deduped] # for print lolz
    print(f"{len(display_flagged_after_dedup)} candidate frames remaining AFTER deduplication.")
    print("Flagged files: ", display_flagged_after_dedup)

    return fullpath_flagged_after_dedup #yepz