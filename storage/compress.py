def compress_image(image, output_path):
    image.save(output_path, "JPEG", quality=70)  # Kompresi sederhana