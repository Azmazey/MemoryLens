from PIL import Image

def apply_rotate(image, angle):
    # angle in degrees (counter-clockwise)
    # expand=True ensures the image size adjusts to fit the rotated image
    return image.rotate(angle, expand=True)

def apply_flip(image, mode):
    # mode: 'horizontal' or 'vertical'
    if mode == 'horizontal':
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    elif mode == 'vertical':
        return image.transpose(Image.FLIP_TOP_BOTTOM)
    return image
