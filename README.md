# English chatbot-tts-nlp

This is a simple chatbot with selectable English proficiency levels, integrated TTS, and a NLP for providing linguistic insights on bot responses.

## Technologies Used
* [Gemini AI](https://deepmind.google/technologies/gemini/#introduction)
* [Flet](https://flet.dev/) with Python
* [Pillow](https://pillow.readthedocs.io/en/stable/) for image processing
* [ElevenLabs API](https://elevenlabs.io/docs/introduction) for TTS functionality
* [Spacy](https://spacy.io/) - NLP

# Installation

Install dependencies:

```
pip install -r requirements.txt
```

Alternatively, you can install the base dependencies individually:

* Flet

```
pip install flet
```

* Generativeai

```
pip install -q -U google-generativeai
```

* PILLOW

```
pip install pillow
```

* spaCy

```
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
```
