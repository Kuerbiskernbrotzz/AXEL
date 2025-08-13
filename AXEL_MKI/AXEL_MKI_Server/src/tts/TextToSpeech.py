import asyncio
import re
import json
import os
import pyttsx3
from pathlib import Path
from logger.logger import log
log.info("tts initialized.")
try:
    from edge_tts import Communicate
    EDGE_TTS_AVAILABLE = True
except ImportError:
    print("Edge tts couldn't be loadet.")
    EDGE_TTS_AVAILABLE = False

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log.info("Error loading the config:", e)
        raise

config = load_config()
SPEAKER = config.get("SPEAKER", "de-DE-KillianNeural")  # Fallback wenn nicht definiert

def remove_markdown(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text.strip()

async def text_to_speech(text, path):
    cleaned_text = remove_markdown(text)
    
    if EDGE_TTS_AVAILABLE:
        try:
            communicate = Communicate(cleaned_text, voice=SPEAKER)
            await communicate.save(path)
            log.info("Speach created sucessfully created.")
            return
        except Exception as e:
            print("edge-tts didn't work, using pyttsx3 instead:", e)

    # Fallback mit pyttsx3
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.save_to_file(cleaned_text, path)
        engine.runAndWait()
        log.info("Speach created sucessfully.")
    except Exception as e:
        log.info("Fehler mit pyttsx3:", e)

# Beispiel:
if __name__ == "__main__":
    asyncio.run(text_to_speech("# Hallo **Welt**! Wie geht's dir?", "output.wav"))






#de-AT-IngridNeural                 Female    General                Friendly, Positive | score: 5.5/10
#de-AT-JonasNeural                  Male      General                Friendly, Positive | score: 6/10
#de-CH-JanNeural                    Male      General                Friendly, Positive | score: 5/10 (Schweitz)
#de-CH-LeniNeural                   Female    General                Friendly, Positive | score: 6/10 (Schweitz)
#de-DE-AmalaNeural                  Female    General                Friendly, Positive | score: 5/10
#de-DE-ConradNeural                 Male      General                Friendly, Positive | score: 9/10 (Kann English)
#de-DE-FlorianMultilingualNeural    Male      General                Friendly, Positive | score: 7/10 (besonders klare stimme)
#de-DE-KatjaNeural                  Female    General                Friendly, Positive | score: 8/10 (Kann English)
#de-DE-KillianNeural                Male      General                Friendly, Positive | score: 8/10 (Kann English)
#de-DE-SeraphinaMultilingualNeural  Female    General                Friendly, Positive | score: 7/10(besonders klare stimme)
