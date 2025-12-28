# floor_map/services.py
import os
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from diffusers import StableDiffusionPipeline
import torch

# Logging
logging.basicConfig(level=logging.INFO)

# Folder for images
UPLOAD_FOLDER = 'floor_map/static/floor_map/generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the model once
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",
        torch_dtype=torch.float32,
        safety_checker=None,
    )
    pipe = pipe.to("cpu")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    pipe = None

def refine_image(image):
    """Post-process the image: sharpen, add grid, labels."""
    sharpened = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
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

def generate_floor_plan(form_data):
    """Main function to generate image based on user input."""
    if pipe is None:
        raise Exception("Model failed to load")
    
    # Build prompt dynamically
    prompt_parts = []
    for key in ['area', 'bedrooms', 'bathrooms', 'parking', 'kitchen', 'living_room']:
        value = form_data.get(key, '').strip()
        if value:
            prompt_parts.append(f"{value} {key}" if not key == 'area' else f"area {value}")
    
    if not prompt_parts:
        raise Exception("Please provide at least one field")
    
    style = form_data.get('style', 'modern').strip()
    user_prompt = ", ".join(prompt_parts)
    full_prompt = f"A highly detailed, accurate architectural floor plan blueprint in {style} style: {user_prompt}. To scale, with measurements, labeled rooms, walls, doors, windows, no furniture, professional CAD-like sketch, top-down view."

    logging.info(f"Generating image for prompt: {full_prompt}")
    image = pipe(full_prompt, num_inference_steps=20, guidance_scale=9.0, height=512, width=512).images[0]
    refined_image = refine_image(image)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"floorplan_{timestamp}.png"
    image_path_full = os.path.join(UPLOAD_FOLDER, image_filename)
    refined_image.save(image_path_full)
    
    return f"floor_map/generated/{image_filename}"
