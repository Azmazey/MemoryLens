from PIL import ImageEnhance

def adjust_saturation(image, value):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(value)