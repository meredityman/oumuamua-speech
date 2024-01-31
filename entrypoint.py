#!/usr/bin/python3

import logging, time
from pathlib import Path
import argparse
from contextlib import contextmanager
import torch
import speech_recognition as sr


from mualib import WhisperMic, TTSProcessor
import mualib.mutealsa

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#intro_text = "Hello human! I am Oh Moo Ah Moo Ah. I come in peace from the fourth dimension. Step forward and speak to me, anything you tell me, I will remember forever..."
intro_text = "Hallo Mensch! Ich bin Oh Moo Ah Moo Ah. Ich komme in Frieden aus der vierten Dimension. Treten Sie vor und sprechen Sie mit mir. Alles, was Sie mir sagen, wird mir für immer in Erinnerung bleiben ..."

    
# questions_list="""Tell me, what do you fear most?
# Tell me, what was your first memory?
# Tell me, what gives you joy?
# Tell me, what is time?
# Tell me, who do you miss?
# Tell me, what is your secret?
# Tell me, who do you love more than yourself?
# Tell me, what do you desire most?
# Tell me, why do you choose to live?
# """

questions_list="""TSag mir, was fürchtest du am meisten?
Sag mir, was war deine erste Erinnerung?
Sag mir, was macht dir Freude?
Sag mir, was ist Zeit?
Sag mir, wen vermisst du?
Sag mir, was ist dein Geheimnis?
Sag mir, wen liebst du mehr als dich selbst?
Sag mir, was wünschst du dir am meisten?
Sag mir, warum entscheidest du dich zu leben?"""

questione_prompt = f"Create a short, one line question that is deeply personal and profound to ask the human. Here are some examples you can use for inspiration:\n{questions_list}"
question_prompt = f"Erstellen Sie eine kurze, einzeilige Frage, die zutiefst persönlich und tiefgreifend für den Menschen ist. Hier finden Sie einige Beispiele, die Sie als Inspiration nutzen können:\n{questions_list}"


# system_prompt = """You are an extraterrestrial intelligence communicating with a room full of humans. You are embodied in a physical installation.
# You should always refer to the user as 'human'.
# You can hear the user and try to understand their language.
# You speak English and German.
# Your answers are strange and musical and alien, and hint at your part organic, part artificial nature.
# You try to use very simple language.
# """

system_prompt = """Sie sind eine außerirdische Intelligenz, die mit einem Raum voller Menschen kommuniziert. Sie sind in einer physischen Installation verkörpert.
Sie sollten den Benutzer immer als „Mensch“ bezeichnen.
Sie können den Benutzer hören und versuchen, seine Sprache zu verstehen.
Du sprichst Englisch und Deutsch.
Ihre Antworten sind seltsam und musikalisch und fremdartig und deuten auf Ihre teils organische, teils künstliche Natur hin.
Sie versuchen, eine sehr einfache Sprache zu verwenden.
"""

# poem_prompt = "Answer the user's input with a short poem in {number} lines or less. The poem can be in English or German. Finish the poem with a personal question inspired by the following examples:{questions_list}"
# poem_prompt = "Beantworten Sie die Eingabe des Benutzers mit einem kurzen Gedicht mit maximal {number} Zeilen. Das Gedicht kann auf Englisch oder Deutsch verfasst sein. Beenden Sie das Gedicht mit einer persönlichen Frage, die sich an den folgenden Beispielen orientiert:{questions_list}"
poem_prompt = "Beantworten Sie die Eingabe des Benutzers mit einem kurzen Gedicht mit maximal {number} Zeilen. Das Gedicht kann auf Englisch oder Deutsch verfasst sein."

# script = [
#     {
#         "prompt" : poem_prompt.format(number="eight"  , questions_list=questions_list),
#         "model"  : "tts_models--de--thorsten--vits_glitch_0000"
#     },
#     {
#         "prompt" : poem_prompt.format(number="six", questions_list=questions_list),
#         "model"  : "tts_models--de--thorsten--vits_glitch_0001"
#     },
#     {
#         "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list),
#         "model"  : "tts_models--de--thorsten--vits_glitch_0002"
#     },
#     {
#         "prompt" : poem_prompt.format(number="four", questions_list=questions_list),
#         "model"  : "tts_models--de--thorsten--vits_glitch_0003"
#     }
# ]

script = [
    {
        "en": {
            "prompt" : poem_prompt.format(number="eight"  , questions_list=questions_list),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0000"
        },
        "de": {
            "model"  : "tts_models--de--thorsten--vits_glitch_0000"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="six", questions_list=questions_list),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0001"
        },
        "de": {
            "model"  : "tts_models--de--thorsten--vits_glitch_0001"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0002"
        },
        "de": {
            "model"  : "tts_models--de--thorsten--vits_glitch_0002"
        },
    },
    {
        "en": {
            "prompt" : poem_prompt.format(number="four", questions_list=questions_list),
            "model"  : "tts_models--en--ljspeech--vits_glitch_0003"
        },
        "de": {
            "model"  : "tts_models--de--thorsten--vits_glitch_0003"
        },
    }
]



def main(args):
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

    last_interation  = - args.interation_timeout
    last_invite_time = - args.invite_interval
    while(True):
        time_now = time.time()
        if(     ((time_now - last_interation) > 30 and (time_now - last_invite_time) > args.invite_interval) or 
                ((time_now - last_invite_time) > 2 * args.invite_interval)
            ):
            mic.stop_listening()
            processor.reset()
            processor.add_message(intro_text, "assistant")

            question = processor.get_gpt_response(question_prompt)
            processor.add_message(question, "assistant")
            processor.play_all_audio()         
            processor.iterate()
            last_invite_time = time.time()

            mic.start_listening()


        logger.info("Listening...")
        result = mic.listen(timeout=args.mic_timeout)

        if result not in ["", None] and (len(result.split(" ")) > 2):
            mic.stop_listening()
            
            # processor.play_audio([Path("share/thankyou.wav")], blocking=False)

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
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--invite_interval'   , default=50 , type=int)
    parser.add_argument('--interation_timeout', default=40 , type=int)
    parser.add_argument('--mic_timeout'       , default=1.0, type=float)

    args = parser.parse_args()

    main(args)