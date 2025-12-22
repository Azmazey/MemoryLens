import os
from datetime import datetime

def save_to_album(image, album_path, format="JPEG", quality=95):
    if not os.path.exists(album_path):
        os.makedirs(album_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Map Pill format to extension
    ext_map = {"JPEG": "jpg", "PNG": "png", "BMP": "bmp"}
    ext = ext_map.get(format.upper(), "jpg")
    
    filename = f"image_{timestamp}.{ext}"
    save_path = os.path.join(album_path, filename)
    
    if format.upper() == "JPEG":
        image.convert("RGB").save(save_path, format=format, quality=quality)
    else:
        image.save(save_path, format=format)
    return save_path