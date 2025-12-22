import os
from datetime import datetime

def save_to_album(image, album_path):
    if not os.path.exists(album_path):
        os.makedirs(album_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image.save(os.path.join(album_path, f"image_{timestamp}.jpg"))