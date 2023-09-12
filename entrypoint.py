#!/usr/bin/python3

import logging
import torch
from TTS.api import TTS
import whisper
from pathlib import Path
import subprocess

def main():
    logging.info(f"Entering {__name__}...")
    logging.info(subprocess.call("nvidia-smi"))
    # Get device

    share_path = Path("share")

    assert(torch.cuda.is_available())
    device = "cuda"

    # List available 🐸TTS models and choose the first one
    model_name = TTS().list_models()[0]
    # Init TTS
    tts = TTS(model_name).to(device)

    # Run TTS
    # ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
    # Text to speech with a numpy output
    wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
    # Text to speech to a file
    tts.tts_to_file(
        text="Hello world!", 
        speaker=tts.speakers[0], language=tts.languages[0], 
        file_path=Path(share_path, "output.wav")
    )


    # wp_model = whisper.load_model("base")

    logging.info(f"Entering {__name__}...")


if __name__ == "__main__":
    main()