import os
import logging
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Set up logging
logger = logging.getLogger(__name__)

# Folder to store generated images (in project static folder)
GENERATED_FOLDER = 'generated'
# Use BASE_DIR to build the path to static/generated/
static_generated_path = os.path.join(settings.BASE_DIR, 'static', GENERATED_FOLDER)
os.makedirs(static_generated_path, exist_ok=True)

# Load the model once (faster, better-quality variant)
pipe = None
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/sd-turbo",  # Faster and sharper for CPU
        torch_dtype=torch.float32,
        safety_checker=None,
    )
    pipe = pipe.to("cpu")  # Change to "cuda" if you have GPU
    logger.info("Stable Diffusion model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    pipe = None

def refine_image(image):
    """Post-process the image for better accuracy: sharpen, add grid, and labels."""
    # Sharpen the image
    sharpened = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    
    # Add a grid overlay for scale reference
    draw = ImageDraw.Draw(sharpened)
    width, height = sharpened.size
    grid_size = 50  # Grid lines every 50 pixels
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill="gray", width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill="gray", width=1)
    
    # Add a simple label (e.g., "Floor Plan")
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Use system font if available
    except:
        font = ImageFont.load_default()
    draw.text((10, 10), "Floor Plan (Illustrative)", fill="black", font=font)
    
    return sharpened

def floor_map_input(request):
    image_path = None
    error_message = None
    
    if request.method == 'POST':
        try:
            # Retrieve and validate form fields (added more for accuracy)
            area = request.POST.get('area', '').strip()
            bedrooms = request.POST.get('bedrooms', '').strip()
            bathrooms = request.POST.get('bathrooms', '').strip()
            parking = request.POST.get('parking', '').strip()
            kitchen = request.POST.get('kitchen', '').strip()
            living_room = request.POST.get('living_room', '').strip()
            style = request.POST.get('style', 'modern').strip()
            
            # Build prompt dynamically
            prompt_parts = []
            if area:
                prompt_parts.append(f"area {area}")
            if bedrooms and bedrooms.isdigit():
                prompt_parts.append(f"{bedrooms} bedrooms")
            if bathrooms and bathrooms.isdigit():
                prompt_parts.append(f"{bathrooms} bathrooms")
            if parking:
                prompt_parts.append(f"parking {parking}")
            if kitchen:
                prompt_parts.append(f"{kitchen}")
            if living_room:
                prompt_parts.append(f"{living_room}")
            
            if not prompt_parts:
                error_message = "Please fill at least one field."
            elif pipe is None:
                error_message = "Model failed to load. Check logs."
            else:
                user_prompt = ", ".join(prompt_parts)
                # More accurate prompt for floor plans
                full_prompt = f"A highly detailed, accurate architectural floor plan blueprint in {style} style: {user_prompt}. To scale, with measurements, labeled rooms, walls, doors, windows, no furniture, professional CAD-like sketch, top-down view."
                
                logger.info(f"Generating image for prompt: {full_prompt}")
                # Generate with better settings
                image = pipe(full_prompt, num_inference_steps=20, guidance_scale=9.0, height=512, width=512).images[0]
                
                # Refine the image
                refined_image = refine_image(image)
                
                # Save with timestamp to the static folder
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"floorplan_{timestamp}.png"
                image_path_full = os.path.join(static_generated_path, image_filename)
                refined_image.save(image_path_full)
                
                # Relative path for template (from static folder)
                image_path = f"{GENERATED_FOLDER}/{image_filename}"  # e.g., "generated/floorplan_20231227_194927.png"
                logger.info(f"Refined image saved: {image_path}")
        
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            error_message = "An error occurred. Please try again."
    
    # Render the template with context
    return render(request, 'floor_map/index.html', {
        'image': image_path,
        'error': error_message,
    })