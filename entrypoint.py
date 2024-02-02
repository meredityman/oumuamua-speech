#!/usr/bin/python3

import logging, time, random
from pathlib import Path
import argparse
from contextlib import contextmanager
import torch
import speech_recognition as sr

from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm

from mualib import WhisperMic, TTSProcessor
from mualib.script import *
import mualib.mutealsa

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(args):
    logger.info(f"Entering Main...")
    # logger.info(subprocess.call("nvidia-smi"))
    # logging.info(subprocess.call("pactl info"))

    def debug_osc(address, *args):
        logging.info(f"OSC Recived: {address}, {args}")

    osc_startup()
    osc_udp_server("0.0.0.0", 3721, "commandserver")
    osc_method("/*", debug_osc, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)


    share_path = Path("share")
    bleeps = [
        Path(share_path, "resources", 'AI Voice SoundFX 01.wav'),
        Path(share_path, "resources", 'AI Voice SoundFX 02.wav'),
        Path(share_path, "resources", 'AI Voice SoundFX 03.wav'),
        Path(share_path, "resources", 'AI Voice SoundFX 04.wav'),
        Path(share_path, "resources", 'AI Voice SoundFX 05.wav')
    ]


    assert(torch.cuda.is_available())
    device = "cuda"

    # with noalsaerr():
    mics_available = sr.Microphone.list_microphone_names()
    mic_index = mics_available.index("pulse")
    if(mic_index is not None):
        mic = WhisperMic(mic_index=mic_index)
    else:
        logging.error(f"Pulse not found! Choose from {mics_available}")
        exit()

    processor = TTSProcessor(script, system_prompt, cache_path = share_path)
    processor.start()

    processor.add_message("System started.", "assistant", "en")
    processor.play_all_audio()

    mic.start_listening()

    last_interation  = - args.interation_timeout
    last_invite_time = - args.invite_interval
    force_intro = False

    def on_note(address, note):
        nonlocal force_intro
        logging.info(f"OSC Recived: {address}, {args}")
        if(note == 60):
            force_intro = True

    osc_method("/Note1", on_note, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

    while(True):
        time_now = time.time()
        osc_process()

        def trigger_intro():
            nonlocal force_intro
            timeout = ((time_now - last_interation) > 30 and (time_now - last_invite_time) > args.invite_interval) or \
                      ((time_now - last_invite_time) > 2 * args.invite_interval)
            
            # return timeout or force_intro
            return force_intro


        # Play invitation
        if( trigger_intro()):
            logging.info("***Play introduction***")
            mic.stop_listening()
            processor.reset()
            processor.add_message(intro_text[args.lang], "assistant", args.lang)

            question = processor.get_gpt_response(question_prompt)
            question, lang = TTSProcessor.get_lang(question, args.lang)
            processor.add_message(question, "assistant", lang=lang)
            processor.play_all_audio()         
            processor.iterate()
            last_invite_time = time.time()
            force_intro = False

            logging.info("***End introduction***")
            mic.start_listening()

        # Listen
        logger.info("Listening...")
        result = mic.listen(timeout=args.mic_timeout)

        if result not in ["", None] and (len(result.split(" ")) > 2):
            mic.stop_listening()
            
            processor.play_audio([random.choice(bleeps)], blocking=False)

            result = result.encode('ascii','ignore').decode("ascii").strip()
            logger.info(f"Result: {result}")

            processor.add_message(result, "user", None)            
            processor.play_all_audio()          
            processor.iterate()
            last_interation = time.time()

            mic.start_listening()

    mic.stop_listening()
    processor.stop() 
    logging.info("Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--invite_interval'   , default=50 , type=int)
    parser.add_argument('--interation_timeout', default=40 , type=int)
    parser.add_argument('--mic_timeout'       , default=1.0, type=float)
    parser.add_argument('--lang'              , default="de", choices=["en", "de"])

    args = parser.parse_args()

    main(args)