#!/usr/bin/python3

import logging, time
from pathlib import Path
from contextlib import contextmanager
import torch
import speech_recognition as sr


from mualib import WhisperMic, TTSProcessor
import mualib.mutealsa

logger = logging.getLogger()
logger.setLevel(logging.INFO)

intro_text = """Hello human! I am Oh Moo Ah Moo Ah. I come in peace from the fourth dimension. Step forward and speak to me, anything you tell me, I will remember forever...
"""


questions_list="""Tell me, what do you fear most?
Tell me, what was your first memory?
Tell me, what gives you joy?
Tell me, what is time?
Tell me, who do you miss?
Tell me, what is your secret?
Tell me, who do you love more than yourself?
Tell me, what do you desire most?
Tell me, why do you choose to live?
"""

question_prompt = f"Create a short, one line question that is deeply personal and profound to ask the human. Here are some examples you can use for inspiration:\n{questions_list}"


system_prompt = """You are an extraterrestrial intelligence communicating with a room full of humans. You are embodied in a physical installation.
You should always refer to the user as 'human'.
You can hear the user and try to understand their language.
Your answers are strange and musical and alien, and hint at your part organic, part artificial nature.
You try to use very simple language.
"""



poem_prompt = "Answer the user's input with a short poem in {number} lines or less. Finish the poem with a personal question inspired by the following examples:{questions_list}"

script = [
    {
        "prompt" : poem_prompt.format(number="eight"  , questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0000"
    },
    {
        "prompt" : poem_prompt.format(number="six", questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0001"
    },
    {
        "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0002"
    },
    {
        "prompt" : poem_prompt.format(number="four", questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0003"
    }
]




def main():
    logger.info(f"Entering Main...")
    # logger.info(subprocess.call("nvidia-smi"))
    # logging.info(subprocess.call("pactl info"))

    share_path = Path("share")

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

    processor.add_message("System started.", "assistant")
    processor.play_all_audio()

    mic.start_listening()

    invite_interval    = 50
    interation_timeout = 40

    last_interation  = - interation_timeout
    last_invite_time = - invite_interval
    while(True):
        time_now = time.time()
        if(     ((time_now - last_interation) > 30 and (time_now - last_invite_time) > invite_interval) or 
                ((time_now - last_invite_time) > 2 * invite_interval)
            ):
            mic.stop_listening()
            processor.reset(script)
            processor.add_message(intro_text, "assistant")

            question = processor.get_gpt_response(question_prompt)
            processor.add_message(question, "assistant")
            processor.play_all_audio()         
            processor.iterate()
            last_invite_time = time.time()

            mic.start_listening()

        logger.info("Listening...")
        result = mic.listen(timeout=1)

        if result not in ["", None] and (len(result.split(" ")) > 2):
            mic.stop_listening()
            
            processor.play_audio([Path("share/thankyou.wav")], blocking=False)

            result = result.encode('ascii','ignore').decode("ascii").strip()
            logger.info(f"Result: {result}")

            processor.add_message(result, "user")            
            processor.play_all_audio()          
            processor.iterate()
            last_interation = time.time()

            mic.start_listening()

    mic.stop_listening()
    processor.stop() 
    logging.info("Exiting...")

if __name__ == "__main__":
    main()