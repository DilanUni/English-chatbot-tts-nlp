from datetime import datetime

AUDIO_PATH_FORMAT = "audios/%Y_%m_%d_%H_%M_%S.mp3"


def chat_format(gemini_response: str) -> str:
    """
    Formats the Gemini response text to fit within a certain line length.
    Parameters:
        gemini_response (str): The Gemini response text.
    Returns:
        str: The formatted Gemini response text.
    """
    max_line_length = 180
    if len(gemini_response) > max_line_length:
        return "\n".join(
            [
                gemini_response[i : i + max_line_length]
                for i in range(0, len(gemini_response), max_line_length)
            ]
        )
    return gemini_response


def output_path_format() -> str:
    """
    Generate the output path format for audio files based on the current date and time.

    Returns:
        str: The output path format for audio files.
    """
    now = datetime.now()
    audio_path = now.strftime(AUDIO_PATH_FORMAT)
    print(audio_path)
    return audio_path


def spacy_text_format(text: str) -> str:
    """
    Removes unnecessary characters for processing by SpaCy

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    characters_to_remove = [
        ",",
        ".",
        "!",
        "?",
        "¿",
        "[",
        "]",
    ]
    cleaned_text = text

    for char in characters_to_remove:
        cleaned_text = cleaned_text.replace(char, "")

    return cleaned_text.strip()
