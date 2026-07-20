import zipfile
import io
import asyncio
import json
from gemini_ocr import extract_vocab
import csv
import genanki
import tempfile

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

# export functions
def export_to_csv(vocab_list):
    """
    vocab_list: list of dicts with keys: vocab_name, reading, meaning
    Returns: bytes of the .csv file (ready to send as a Discord attachment)
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Word", "Reading", "Meaning"])  # header row
 
    for word in vocab_list:
        writer.writerow([word["vocab_name"], word["reading"], word["meaning"]])
 
    return output.getvalue().encode("utf-8")

def export_to_anki(vocab_list):
    """
    vocab_list: list of dicts with keys: vocab_name, reading, meaning
    Returns: bytes of the .apkg file (ready to send as a Discord attachment)
    """
    MODEL_ID = 8379216775
    DECK_ID = 5211807228

    model = genanki.Model(
        MODEL_ID,
        "Japanese Vocab Model",
        fields=[
            {"name": "Word"},
            {"name": "Reading"},
            {"name": "Meaning"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Word}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Reading}}<br>{{Meaning}}',
            }
        ],
    )
 
    deck = genanki.Deck(deck_id = DECK_ID, name = "Page_Translation") 
 
    for word in vocab_list:
        note = genanki.Note(
            model = model,
            fields = [word["vocab_name"], word["reading"], word["meaning"]],
        )
        deck.add_note(note)
    
    with tempfile.NamedTemporaryFile(suffix = ".apkg") as tmp:
        genanki.Package(deck).write_to_file(tmp.name)
        tmp.seek(0)
        return tmp.read()

    return tmp.read()
 

