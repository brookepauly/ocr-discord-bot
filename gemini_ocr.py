from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def extract_vocab(images: list[tuple[str, bytes, str]]):
    """
    Parameters:
    images: list of (filename, image_bytes, mime_type) tuples

    Return:
    (JSON text): vocab list of word, reading, and meaning per image

    Sends multiple images to Gemini in one request and returns
    extracted vocab as JSON.
    """
    parts = [
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        for name, image_bytes, mime_type in images
    ]

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        config={
            "system_instruction": (
                "You will receive multiple images of Japanese book pages. "
                "Extract Japanese vocabulary from each page image. "
                "For every highlighted word on each page, return: word, reading (hiragana), meaning (English). "
                "Be very careful not to miss any highlighted words. "
                "Output as JSON only, no other text."
            )
        },
        contents=parts,
    )
    return response.text