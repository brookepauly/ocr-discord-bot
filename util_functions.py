import zipfile
import io
import asyncio
import json
from gemini_ocr import extract_vocab

VALID_IMAGE_EXTS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

# potential room for errors with "ghost files"
def extract_images_from_zip(zip_bytes: bytes):
    """
    Takes raw zip bytes, returns list of (filename, image_bytes, mime_type)
    for every valid image inside. Skips folders/hidden files automatically.
    """
    images = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            if name.endswith("/") or name.startswith("__MACOSX/"):
                continue

            ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
            if ext not in VALID_IMAGE_EXTS:
                continue

            with z.open(name) as f:
                images.append((name, f.read(), VALID_IMAGE_EXTS[ext]))

    return images


async def process_images(images, batch_size = 2):
    """
    images: list of (filename, image_bytes, mime_type)
    Returns: all_vocab (list of extracted word dicts)
    """
    all_vocab = []
    for i in range(0, len(images), batch_size):
        chunk = images[i:i + batch_size]
        raw_result = extract_vocab(chunk)
        vocab_list = json.loads(raw_result)["vocab"]
        all_vocab.extend(vocab_list)
        await asyncio.sleep(4)

    return all_vocab