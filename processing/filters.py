from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

def apply_neutral_filter(image):
    """No filter - returns original image"""
    return image.copy()

def apply_warm_filter(image):
    """Apply warm filter - adds orange/yellow tones"""
    # Ensure RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array for manipulation
    img_array = np.array(image, dtype=np.float32)
    
    # Add warm tones (increase red and green, slightly decrease blue)
    img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.15, 0, 255)  # Red
    img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.05, 0, 255)  # Green
    img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 0.9, 0, 255)   # Blue
    
    return Image.fromarray(img_array.astype(np.uint8))

def apply_cold_filter(image):
    """Apply cold filter - adds blue tones"""
    # Ensure RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Add cool tones (decrease red, slightly increase green and blue)
    img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 0.85, 0, 255)  # Red
    img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.0, 0, 255)   # Green
    img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 1.2, 0, 255)   # Blue
    
    return Image.fromarray(img_array.astype(np.uint8))

def apply_vintage_filter(image):
    """Apply vintage filter - sepia tone with slight vignette"""
    # Ensure RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Apply sepia tone matrix
    sepia_r = img_array[:, :, 0] * 0.393 + img_array[:, :, 1] * 0.769 + img_array[:, :, 2] * 0.189
    sepia_g = img_array[:, :, 0] * 0.349 + img_array[:, :, 1] * 0.686 + img_array[:, :, 2] * 0.168
    sepia_b = img_array[:, :, 0] * 0.272 + img_array[:, :, 1] * 0.534 + img_array[:, :, 2] * 0.131
    
    img_array[:, :, 0] = np.clip(sepia_r, 0, 255)
    img_array[:, :, 1] = np.clip(sepia_g, 0, 255)
    img_array[:, :, 2] = np.clip(sepia_b, 0, 255)
    
    sepia_img = Image.fromarray(img_array.astype(np.uint8))
    
    # Reduce contrast slightly for vintage look
    enhancer = ImageEnhance.Contrast(sepia_img)
    sepia_img = enhancer.enhance(0.9)
    
    return sepia_img

def apply_bw_filter(image):
    """Apply black and white filter - high contrast grayscale"""
    # Convert to grayscale
    bw_img = image.convert('L')
    
    # Increase contrast for dramatic B&W
    enhancer = ImageEnhance.Contrast(bw_img)
    bw_img = enhancer.enhance(1.2)
    
    # Convert back to RGB mode for consistency
    return bw_img.convert('RGB')
