import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

CHUNK_SIZE = 1024


def load_configuration():
    """Load environment variables and return API key and voice ID.

    Returns:
        tuple: A tuple containing the API key and voice ID.
    """
    load_dotenv()
    voice_id = os.getenv("VOICE_ID")
    xi_api_key = os.getenv("XI_API_KEY")
    return voice_id, xi_api_key


def build_tts_request(text: str):
    """Build the request data for text-to-speech conversion.

    Args:
        text (str): The text to be converted to speech.

    Returns:
        tuple: A tuple containing the TTS URL, headers, and request data.
    """
    voice_id, xi_api_key = load_configuration()

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {"Accept": "application/json", "xi-api-key": xi_api_key}

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    return tts_url, headers, data


def tts(
    text: str,
    output_path: str,
):
    """
    Convert text to speech and save the audio stream to a file.

    Args:
        text (str): The text to be converted to speech.
        output_path (str): The path where the audio stream will be saved.
    """

    tts_url, headers, data = build_tts_request(text)
    response = requests.post(url=tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print("Audio stream saved successfully.")
    else:
        raise RuntimeError(
            "Failed to convert text to speech. Error message: {}".format(response.text)
        )
