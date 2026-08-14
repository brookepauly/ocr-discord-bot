from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field


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
        for _, image_bytes, mime_type in images # _ = ignoring name of file
    ]

    class Vocab(BaseModel):
        vocab_name: str = Field(description="The vocab word.")
        reading: str = Field(description="Hiragana for the vocabulary reading.")
        meaning: str = Field(description="English translation/meaning of the vocab word")

    class VocabList(BaseModel):
        vocab: list[Vocab]

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        config={
            "system_instruction": (
                "You will receive multiple images of Japanese book pages. "
                "Extract Japanese vocabulary from each page image. "
                "For every highlighted word on each page, return: word, reading (hiragana), meaning (English). "
                "Double check pages to make sure nothing is missed."
            ),
            "response_mime_type": "application/json",
            "response_schema": VocabList,
        },
        contents = parts,
    )
    return response.text