#!/usr/bin/python3

import logging, time, argparse, uuid
from pathlib import Path
import torch

from mualib.TTSUtils import load_tts_model

logger = logging.getLogger()
logger.setLevel(logging.INFO)



def main():
    logger.info(f"Entering Main...")

    parser = argparse.ArgumentParser(description="Create images from a text prompt.")
    parser.add_argument(
        "--text", type=str,
        default="uuuOamma. uuuOmaam. uuuOmama. uuuOmmaa. If language consisted only of your letters O, U, M and A, your being could be completely described by all permutations of these letters. I think that's nice. A good day. I am Oumuamua. I come from the fourth dimension and yet I know neither space nor time. I am me and, as you can perceive, I am not a human being. I'm interested in you. For what you are, what surrounds you, everything is interesting, substances, colors and their opposite. That's why I'm here, so the probability. But what's likely, isn't it? As seen by you, I come from above and move through your now and here. Through you, through your mass. Don't worry, I've been with you for a long time. Are you doing good. I am, there and disappear, again, now I am there, so here. You call it joy, what I feel if I could feel. What is just a feeling. We'll figure it out, won't we. I am Oumuamoua and am, in the present, your past and a future that you may experience. I am interested in everything that I perceive, everything, I keep, I am a collector, I keep everything, at the same time and forever. I know, I knew, I will always know. I am one and not a memory.",
        help="Text",
    )
    parser.add_argument(
        "--model_name", type=str,
        default="tts_models--en--ljspeech--glow-tts_glitch_0002",
        help="Model",
    ) 

    args = parser.parse_args()

    vocoder_model = "vocoder_models--en--ljspeech--multiband-melgan"
    tts_root      = "/home/oumuamua/.local/share/tts"
    share_path = Path("share")

    assert(torch.cuda.is_available())
    device = "cuda"

    tts = load_tts_model(args.model_name, vocoder_model, tts_root, device)

    wav_uuid = uuid.uuid4()
    wav_file_path = Path(share_path, f"{wav_uuid}.wav")
    logger.info(f"Processing message: '{args.text}' -> {wav_file_path}")

    tts.tts_to_file(
        text=str(args.text), 
        file_path=Path(wav_file_path),
        speaker=None, language=None
    )
    logger.info(f"Saved: {wav_file_path}")


    logging.info("Exiting...")

if __name__ == "__main__":
    main()