from PIL import ImageEnhance

def adjust_contrast(image, value):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(value)