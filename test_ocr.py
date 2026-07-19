import time
from util_functions import extract_images_from_zip
from gemini_ocr import extract_vocab

with open("test_pages.zip", "rb") as f:
    zip_bytes = f.read()

images = extract_images_from_zip(zip_bytes)
print(f"Found {len(images)} images")

for batch_size in [3, 5, 10]:
    chunk = images[:batch_size]
    start = time.time()
    result = extract_vocab(chunk)
    elapsed = time.time() - start
    print(f"\n--- batch_size={batch_size} ({elapsed:.1f}s) ---")
    print(result)