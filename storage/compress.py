def compress_image(image, output_path, quality=70):
    # Ensure RGB for JPEG
    if output_path.lower().endswith(('.jpg', '.jpeg')):
        image = image.convert("RGB")
    image.save(output_path, quality=quality, optimize=True)