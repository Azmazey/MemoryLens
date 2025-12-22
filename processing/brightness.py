from PIL import ImageEnhance

def adjust_brightness(image, value):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(value)
