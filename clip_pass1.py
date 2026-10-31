import glob
import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1" # disable progress bar
os.environ["HF_HUB_VERBOSITY"] = "error" # hide the huggingface HF_TOKEN warning

import time
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor, logging
import rich.progress as rp
from rich.console import Console
console = Console()

logging.set_verbosity_error() # hide other potential transformer warnings for different versions, and makes it so that only errors are shown
logging.disable_progress_bar() # counter-measure, for different versions (users)

# minimum cosine similarity for a frame to be considered a suggestive prompt
MIN_SUGGESTIVE_COSINE = 0.25

NUM_THREADS = 6

# minimum suggestive score OVER the top safe score
MARGIN_THRESHOLD = 0.03
# default is 0.03 for a clean ratio
# lower it to 0.025-0.027 for stubborn frames, 0.015 or lower for the most stubborn ones if:
# 1. u can skim through god-knows how many more frames get their way through, AND/OR, u have Pass2 enabled (possibly with good gpu/api, future update).

DEDUPE_SIMILARITY_THRESHOLD = 0.93 # dedup
DEDUPE_KEEP_SECONDS = 2   # similar frames closer than this are kept

EXTRA = False   # Default = False. True = print full detail for every frame e.g. sug_cos, safe_cos, and likes. False = no print

SAFE_LABELS = [
    # character & everyday attire
    "an anime character's face or headshot talking",
    "an anime character in school uniform, jacket, hoodie, sweater, or winter coat",
    "a group of fully clothed anime characters standing or sitting together",
    "an anime character walking, running, sitting, or eating normally",

    # specific backgrounds & scene props
    "white plastic garbage bags, trash cans, or a green protective mesh net",
    "a birdcage, cloth cover, hanging curtain, or lamp shade",
    "abstract colorful circles, dots, patterns, geometry, or anime title graphics",
    "an empty anime school hallway, classroom, windows, or building corridor",
    "anime scenery, landscape, street, trees, blue sky, or clouds",
    "household furniture, table, desk, chair, room walls, or floor",
    "a close-up shot of small inanimate objects, books, or papers",

    # junk types found in testing (by common-ing out frames into types)
    "a close-up of an anime character's hair or the back of their head",
    "a wooden stick, sword, or object in fast motion",
    "a close-up of plain cloth, fabric, or a textured pattern",
    "a male anime character, a boy, sitting, sleeping, or walking",
    "a chibi super-deformed cartoon character with tiny cute proportions",
    "a small cute anime child or toddler"

]

SUGGESTIVE_LABELS = [
    # directly exposed & swimwear
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

def frame_time(path, times): # fetches the index position of the respective frame's time in the times list. explained below.
    number = int(os.path.basename(path)[6:-4])
    return float(times[number - 1])

def dedupe_flagged(flagged, times): # used later for deduplication
    deduped = []
    for path, features in flagged: # for each. (a reminder uh nvm)
        if deduped: # checks if empty or not. skips for first frame.
            prev_path, prev_features = deduped[-1]
            similarity = (features @ prev_features.t()).item()
            gap = frame_time(path, times) - frame_time(prev_path, times) # time passed between two frames... working: "frame0044.jpg" --> 44 --> sent to "times" list to find the position/index but - 1 = 43 as first idx = 0 --> that exact time for that frame's position in seconds is indexed out as str --> float
            if similarity > DEDUPE_SIMILARITY_THRESHOLD and gap > DEDUPE_KEEP_SECONDS:
                continue # if above line is true, it doesn't append the frame, hence removing it. mission accomplished.
        deduped.append((path, features))
    return deduped


def flag_clip(times, margin_threshold=MARGIN_THRESHOLD, threads=NUM_THREADS, extra=EXTRA):

    torch.set_num_threads(threads) # custom thread count for multicore CPU

    with console.status("[bold green]Loading CLIP model..."):
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip_model.eval()
    console.print("[green]✓[/green] [dim]CLIP model loaded[/dim]")

    # precomputing text embeddings once
    text_inputs = clip_processor(text=ALL_LABELS, return_tensors="pt", padding=True) # type: ignore     # ts a dict consisting of input ids n stuff

    with torch.inference_mode():
        # pass through text model then project to latent space
        text_outputs = clip_model.text_model(**text_inputs) # a whole ahh custom object
        pooled_text = text_outputs.pooler_output # shape: (num_labels, 512). it's a hidden part of the above-mentioned custom object, a 2D tensor by itself made of many summary vectors (1D tensors), one summary vector per label.
        text_embeds = clip_model.text_projection(pooled_text) # 512 --> 512. realigns the text (1D summary tensors) vectors and projects them in latent comparable space of labels-image comparison
        text_features = F.normalize(text_embeds, p=2, dim=-1) # removes the raw size (magnitude) and only allow what is needed (direction/meaning, nothing else)

    frames = sorted(glob.glob("frames/*.jpg")) # find and sort
    total = len(frames)
    if extra:
        console.print(f"[dim]Total frames: {total}[/dim]")

    flagged = []
    start = time.time() # timestamp captured once, right before the loop begins

    # noinspection PyTypeChecker, PyArgumentList
    progress = rp.Progress(
        rp.SpinnerColumn(style="cyan"),
        rp.TextColumn("{task.description}"),
        rp.BarColumn(complete_style="cyan", finished_style="green"),
        rp.MofNCompleteColumn(),
        rp.TimeRemainingColumn(),
        console=console,
    )
    with progress:
        for count, path in enumerate(progress.track(frames, description="Scanning frames"), start=1):  # a normal loop, but with an automatic counter (i.e. 2 vars instead of js 1) + tracked using Rich progress module
            frame_name = os.path.basename(path) # to print the raw file name instead of the full path (at 2 places)
            image = Image.open(path).convert("RGB") # "method chaining" 1 --> open and decode image file. 2 --> converts to RGB color mode. i.e. two instances. 1st temp, 2nd perm. Only the second instance is stored in 'image'

            entropy = get_image_entropy(image)
            dynamic_min_cos = MIN_SUGGESTIVE_COSINE + (0.010 if entropy < 5.0 else 0.0)
            dynamic_margin = margin_threshold + (0.005 if entropy < 5.0 else 0.0)

            image_inputs = clip_processor(images=image, return_tensors="pt") # type: ignore

            with torch.inference_mode():
                # pass through vision model then project to latent space
                image_outputs = clip_model.vision_model(**image_inputs)
                pooled_image = image_outputs.pooler_output # shape: (1, 768). a 2D tensor holding the 1 summary vector for the ONE frame.
                image_embeds = clip_model.visual_projection(pooled_image) # projection shrinks the tensor shape from (1,768) to (1, 512) so it (image tensor) can be projected in "latent comparable space of labels-image comparison"
                image_features = F.normalize(image_embeds, p=2, dim=-1)


                # cosine similarity matmul:
                cosine_sims = (image_features @ text_features.t())[0]

            max_suggestive_cos = cosine_sims[len(SAFE_LABELS):].max().item()
            max_safe_cos = cosine_sims[: len(SAFE_LABELS)].max().item()

            margin = max_suggestive_cos - max_safe_cos
            is_candidate = (max_suggestive_cos >= dynamic_min_cos) and (margin >= dynamic_margin)

            if is_candidate:
                flagged.append((path, image_features)) #  !!!!  both the path and the 1D summary vector.  !!!!

            if extra:
                tag = "FLAG" if is_candidate else "safe"
                console.print(
                    f"[{count}/{total}] {frame_name}: sug_cos={max_suggestive_cos:.3f} "
                    f"safe_cos={max_safe_cos:.3f} margin={margin:+.3f} (ent={entropy:.1f}) {tag} | "
                    f"flagged: {len(flagged)}",
                )

    deduped = dedupe_flagged(flagged, times)

    if extra:
        print(f"\nDone in {time.time() - start:.1f}s.")

        print(f"{len(flagged)}/{total} candidate frames BEFORE deduplication.")
        print(f"{len(deduped)}/{len(flagged)} candidate frames remaining AFTER deduplication.")

    flagged = [path for path, _ in deduped]  # full path string
    return flagged