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
        help="Text",
    )
    parser.add_argument(
        "--name", type=str,
        help="Filename",
    )
    parser.add_argument(
        "--model_name", type=str,
        help="Model",
    ) 

    args = parser.parse_args()
    print(args)

    # vocoder_model = "vocoder_models--en--ljspeech--multiband-melgan"
    tts_root      = "/home/oumuamua/.local/share/tts"
    share_path = Path("share")

    assert(torch.cuda.is_available())
    device = "cuda"

    tts = load_tts_model(args.model_name, None, tts_root, device)

    if(args.name):
        wav_file_path = Path(share_path, f"{args.name}.wav")
    else:
        wav_uuid = uuid.uuid4()
        wav_file_path = Path(share_path, f"{wav_uuid}.wav")
    logger.info(f"Processing message: '{args.text}' -> {wav_file_path}")

    tts.tts_to_file(
        text=str(args.text), 
        file_path=Path(wav_file_path)
    )
    logger.info(f"Saved: {wav_file_path}")


    logging.info("Exiting...")

if __name__ == "__main__":
    main()