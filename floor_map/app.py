# floor_map/services/generator.py

import torch
import os
import logging
from datetime import datetime
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings

logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, "generated")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model ONCE (safe)
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float32,
        safety_checker=None,
    ).to("cpu")
    logging.info("Stable Diffusion model loaded.")
except Exception as e:
    logging.error(e)
    pipe = None


def refine_image(image):
    sharpened = image.filter(
        ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3)
    )

    draw = ImageDraw.Draw(sharpened)
    width, height = sharpened.size
    grid_size = 50

    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill="gray", width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill="gray", width=1)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((10, 10), "Floor Plan (Illustrative)", fill="black", font=font)
    return sharpened


def generate_floor_plan(data):
    if pipe is None:
        raise Exception("Model not loaded")

    prompt_parts = []

    if data.get("area"):
        prompt_parts.append(f"area {data['area']}")
    if data.get("bedrooms"):
        prompt_parts.append(f"{data['bedrooms']} bedrooms")
    if data.get("bathrooms"):
        prompt_parts.append(f"{data['bathrooms']} bathrooms")
    if data.get("parking"):
        prompt_parts.append(f"parking {data['parking']}")
    if data.get("kitchen"):
        prompt_parts.append(data["kitchen"])
    if data.get("living_room"):
        prompt_parts.append(data["living_room"])

    user_prompt = ", ".join(prompt_parts)
    style = data.get("style", "modern")

    full_prompt = (
        f"A highly detailed architectural floor plan blueprint in {style} style: "
        f"{user_prompt}, to scale, labeled rooms, CAD drawing, top-down view"
    )

    image = pipe(
        full_prompt,
        num_inference_steps=20,
        guidance_scale=9.0,
        height=512,
        width=512
    ).images[0]

    image = refine_image(image)

    filename = f"floorplan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    return f"generated/{filename}"
