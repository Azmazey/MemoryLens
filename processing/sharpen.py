from PIL import ImageFilter

def apply_sharpen(image, factor=1.0):
    # factor 0.0 = original
    # factor 1.0 = standard sharpen
    # We map factor to percent: factor 1.0 -> 150%, factor 2.0 -> 300%
    # If factor is 0, we return original image to save processing.
    if factor <= 0:
        return image
    
    # Base params: radius=2, threshold=3 (standard unsharp mask)
    # Strength is controlled by 'percent'.
    percent_value = int(factor * 150) # Scale arbitrarily
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=percent_value, threshold=3))