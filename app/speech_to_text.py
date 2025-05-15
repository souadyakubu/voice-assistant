import openai
from config import OPENAI_API_KEY

def speech_to_text(audio_path):
    openai.api_key = OPENAI_API_KEY
    response = openai.Audio.transcriptions.create(
        file=open(audio_path, "rb"),
        model="whisper-1"
    )
    return response['text']