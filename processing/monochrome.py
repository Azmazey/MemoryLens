from PIL import Image

def apply_monochrome(image, factor=1.0):
    # factor 0.0 = original color
    # factor 1.0 = full grayscale
    
    # Ensure image is in RGB mode for blending
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert to grayscale and back to RGB
    grayscale = image.convert("L").convert("RGB")
    
    # Blend the images (both are now guaranteed to be RGB and same size)
    return Image.blend(image, grayscale, factor)