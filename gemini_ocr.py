from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def extract_vocab(image_bytes: bytes, mime_type: str = "img/jpeg"):
    """
    Parameters: 

    bytes (int/str): list of binary aka bytes of file
    mime_type (str): standardized label of what bytes represent

    Return:
    (JSON): vocab list of word, reading, and meaning
    
    Insert image, put it through gemini 3.1 flash, and return 
    translated JSON of image vocab cards.
    """
    response = client.models.generate_content(
        model = "gemini-3.1-flash-lite",
        config={
        "system_instruction": (
                "Extract Japanese vocabulary from this book page image. "
                "For each highlighted word, return: word, reading (hiragana), meaning (English), "
                "Output as JSON only, no other text."
            )
        },
        contents=[
            types.Part.from_bytes(data = image_bytes, mime_type = mime_type),
        ]
    )
    return response.text