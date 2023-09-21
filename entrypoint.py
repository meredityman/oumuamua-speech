#!/usr/bin/python3

import os, logging, time, platform, queue, threading, uuid, sys, subprocess
from pathlib import Path
import numpy as np
from contextlib import contextmanager
import torch
import pyaudio
import speech_recognition as sr
from TTS.api import TTS
import openai
import whisper
from random import shuffle


logger = logging.getLogger()
logger.setLevel(logging.INFO)


openai.api_key = open("/home/oumuamua/openai.key").read()


intro_text = """Hello human! I am Oh Moo Ah Moo Ah. I come in peace from the fourth dimension. You can speak to me, anything you tell me, I will remember forever...
"""


questions_list="""What do you fear most?
What was your first memory?
What gives you joy?
What is time?
Who do you miss?
What makes you tick?
What is your secret?
Who do you love more than yourself?
What do you desire most?
Why do you choose to live?
"""

question_prompt = f"Create a short, one line question that is deeply personal and profound to ask the human. Here are some examples you can use for inspiration:\n{questions_list}"


system_prompt = """You are an extraterrestrial intelligence communicating with a room full of humans. You are embodied in a physical installation.
You should always refer to the user as 'human'.
You can hear the user and try to understand their language.
Your answers are strange and musical and hint at your part organic, part artificial nature.
You try to use very simple language.
"""



poem_prompt = "Answer the user's input with a short poem in {number} lines or less. Finish the poem with a question inspired by the following examples:{questions_list}"

script = [
    {
        "prompt" : poem_prompt.format(number="six"  , questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0000"
    },
    {
        "prompt" : poem_prompt.format(number="eight", questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0001"
    },
    {
        "prompt" : poem_prompt.format(number="ten"  , questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0002"
    },
    {
        "prompt" : poem_prompt.format(number="twelve", questions_list=questions_list),
        "model"  : "tts_models--en--ljspeech--glow-tts_glitch_0003"
    }
]

# def pyaudio_test():
#     p = pyaudio.PyAudio()

#     # Record
#     stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
#     print("Recording...")
#     frames = []
#     for i in range(0, int(p.get_device_info_by_index(1)['defaultSampleRate'] / 1024 * 5)):
#         data = stream.read(1024)
#         frames.append(data)
#     stream.stop_stream()
#     stream.close()
#     print("Recording finished.")

#     # Play
#     stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
#     print("Playing back...")
#     for frame in frames:
#         stream.write(frame)
#     stream.stop_stream()
#     stream.close()

#     # Close PyAudio
#     p.terminate()

class WhisperMic:
    def __init__(self,model="base",device=("cuda" if torch.cuda.is_available() else "cpu"),english=False,verbose=False,energy=300,pause=0.8,dynamic_energy=False,mic_index=None):
        # self.logger = get_logger("whisper_mic", "info")
        self.logger = logger
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.verbose = verbose
        self.english = english
        self.phrase_time_limit = 5
        # self.keyboard = pynput.keyboard.Controller()

        self.platform = platform.system()

        if (model != "large" and model != "large-v2") and self.english:
            model = model + ".en"
        

        logger.info("Loading Whisper...")
        self.audio_model = whisper.load_model(model).to(device)

        self.result_queue: "queue.Queue[str]" = queue.Queue()

        self.mic_active  = False
        self.audio_queue = None

        self.banned_results = [""," ","\n",None]

        logger.info("Setting up Mic...")
        self.setup_mic(mic_index)


    def setup_mic(self, mic_index):
        if mic_index is None:
            self.logger.info("No mic index provided, using default")
        self.source = sr.Microphone(sample_rate=16000, device_index=mic_index)

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.energy
        self.recorder.pause_threshold  = self.pause
        self.recorder.dynamic_energy_threshold = self.dynamic_energy
        self.stop_callback = None


    def start_listening(self):
        
        if self.mic_active:
            raise

        self.audio_queue = queue.Queue()

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

        self.mic_active = True
        self.stop_callback = self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.phrase_time_limit)
        self.logger.info("Mic setup complete, you can now talk")

    def stop_listening(self):

        if not self.mic_active:
            raise
        self.stop_callback(True)
        self.stop_callback = None
        self.mic_active = False
        # self.audio_queue.join()
        self.audio_queue = None

    def listen(self, timeout: int = 1):
        if(self.mic_active):
            audio_data = self.get_all_audio(timeout)
            self.transcribe(data=audio_data)
            while True: 
                try:
                    return self.result_queue.get(block=True, timeout=1)
                except queue.Empty:
                    return None
        else:
            time.sleep(timeout)


    def preprocess(self, data):
        return torch.from_numpy(np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0)

    def get_all_audio(self, min_time: float = -1.):
        audio = bytes()
        got_audio = False
        time_start = time.time()
        while not got_audio or time.time() - time_start < min_time:
            try:
                audio += self.audio_queue.get(timeout=min_time)
            except queue.Empty:
                got_audio = True
            
        data = sr.AudioData(audio,16000,2)
        data = data.get_raw_data()
        return data


    def record_callback(self,_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.audio_queue.put_nowait(data)


    def transcribe(self,data=None, realtime: bool = False) -> None:
        if data is None:
            return

        audio_data = data
        audio_data = self.preprocess(audio_data)
        if self.english:
            result = self.audio_model.transcribe(audio_data,language='english')
        else:
            result = self.audio_model.transcribe(audio_data)

        predicted_text = result["text"]
        if not self.verbose:
            if predicted_text not in self.banned_results:
                self.result_queue.put_nowait(predicted_text)
        else:
            if predicted_text not in self.banned_results:
                self.result_queue.put_nowait(result)





class TTSProcessor:
    def __init__(self, tts_root = "/home/oumuamua/.local/share/tts", cache_path = "/tmp", device = "cuda"):
        self.tts_root = Path(tts_root)
        self.cache_path = cache_path
        self.device = device
        self.tts    = None
        self.vocoder_model = "vocoder_models--en--ljspeech--multiband-melgan"
        self.loaded_model  = None
        self.desired_model = None
        self.script_line = None

        self.reset()

        self.file_lock = threading.Lock()
        self.ready_files = []

        self.message_queue  = queue.Queue()
        self.response_queue = queue.Queue()

    def start(self):
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_queue)
        self.processing_thread.start()

    def reset(self):
        assert(len(script) > 1)
        self.history = []
        self.script  = script.copy()
        self.desired_model = "tts_models--en--ljspeech--glow-tts"
        self.load_model(self.desired_model)

    def iterate(self):
        self.script_line   = self.script.pop(0)
        self.desired_model = self.script_line["model"]
        if(len(self.script) == 0):
            logger.warning("Finished script")
            self.reset()


    def load_model(self, model):
        # model = self.script_line["model"]

        model_path           = Path(self.tts_root, model, "model_file.pth")
        assert(model_path.exists())

        if(self.tts and self.tts.synthesizer.tts_checkpoint == model_path):
            return

        config_path          = Path(self.tts_root, model, "config.json")
        assert(config_path.exists())
        vocoder_path         = Path(self.tts_root, self.vocoder_model, "model_file.pth")
        assert(vocoder_path.exists())
        _vocoder_config_path = Path(self.tts_root, self.vocoder_model, "config.json")
        vocoder_config_path  = Path(self.tts_root, self.vocoder_model, "_config.json")


        logger.info(f"Loading model {model}")

        with open(_vocoder_config_path, 'r') as file:
            data = file.read()
        data = data.replace('/home/meredityman/', '/home/oumuamua/')
        with open(vocoder_config_path, 'w') as file:
            file.write(data)

        # Init TTS
        self.tts = TTS(
            model_name            = "tts_models/en/ljspeech/glow-tts",
            model_path            = model_path         ,
            config_path           = config_path        ,
            vocoder_path          = vocoder_path       ,
            vocoder_config_path   = vocoder_config_path
        ).to(self.device)

        self.loaded_model = model

    def add_message(self, message, role):
        self.file_lock.acquire()
        if(role == "user"):
            self.message_queue.put(message)
        elif(role == "assistant"):
            self.response_queue.put(message)

    def play_all_audio(self, timeout=-1):
        if self.file_lock.acquire(blocking=True, timeout=timeout):
            files, self.ready_files = self.ready_files, []
            self.file_lock.release()
            self.play_audio(files)
    

    
    def process_queue(self):
        while self.running:
            if(self.script_line):
                if(self.script_line["model"] != self.loaded_model):
                    self.load_model(self.script_line["model"] )

            try:
                message = self.message_queue.get(timeout=0.2)
                if(message):
                    response_message = self.process_message(message)
                    self.response_queue.put_nowait(response_message)
            except queue.Empty:
                # logging.warn("Message timeout")
                pass

            try:
                response_message = self.response_queue.get(timeout=0.2)
                if(response_message):
                    self.speak(response_message)
                    self.file_lock.release()
            except queue.Empty:
                # logging.warn("Response timeout")
                pass


            # self.iterate()                
    def play_audio(self, wav_files):
        wav_files = [str(f.resolve()) for f in wav_files]
        logger.info(f"Playing: {', '.join(wav_files)}")
        play_proc = subprocess.Popen(["aplay"] + wav_files)
        play_proc.communicate()
        logger.info("Finished Speaking")
            
    def process_message(self, message):

        self.history += [{"role": "user", "content": f'{message}'}]
        prompt = self.script_line["prompt"]

        return self.get_gpt_response(prompt)

    def get_gpt_response(self, prompt):
        while(True):
            try:
                messages = [{"role": "system", "content": system_prompt}]
                messages += [ m for m in self.history]
                messages += [ {"role": "system", "content": f'{prompt}'}]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages)

                return response.choices[0].message.content
            except Exception as e:
                logging.warn(e.decode())
                time.sleep(1.0)

    def speak(self, response_message):
        wav_uuid = uuid.uuid4()
        wav_file_path = Path(self.cache_path, f"{wav_uuid}.wav")
        logger.info(f"Processing message: '{response_message}' -> {wav_file_path}")
        try:
            self.tts.tts_to_file(
                text=response_message, 
                file_path=Path(wav_file_path)
            )
            logger.info(f"Saved: {wav_file_path}")
            self.ready_files.append(wav_file_path)
        except Exception as e:
            logger.error(e)

    def stop(self):
        self.running = False
        self.processing_thread.join()




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


    processor = TTSProcessor(cache_path = share_path)
    processor.start()



      
    processor.add_message("System started.", "assistant")
    processor.play_all_audio()


    mic.start_listening()

    invite_interval    = 40
    interation_timeout = 30

    last_interation  = - interation_timeout
    last_invite_time = - invite_interval
    while(True):
        time_now = time.time()
        if((time_now - last_interation) > 30 and (time_now - last_invite_time) > invite_interval):
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
        result = mic.listen(timeout=1)

        if result not in ["", None]:
            mic.stop_listening()

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