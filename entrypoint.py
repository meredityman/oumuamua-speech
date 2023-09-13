#!/usr/bin/python3

import os, logging, time, platform, queue, threading, uuid
import numpy as np
from pathlib import Path
import subprocess
from ctypes import *
from contextlib import contextmanager
import torch
import pyaudio
import speech_recognition as sr
from TTS.api import TTS
import whisper



ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

class WhisperMic:
    def __init__(self,model="base",device=("cuda" if torch.cuda.is_available() else "cpu"),english=False,verbose=False,energy=300,pause=0.8,dynamic_energy=False,save_file=False,mic_index=None):
        # self.logger = get_logger("whisper_mic", "info")
        self.logger = logging
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.save_file = save_file
        self.verbose = verbose
        self.english = english
        # self.keyboard = pynput.keyboard.Controller()

        self.platform = platform.system()

        if (model != "large" and model != "large-v2") and self.english:
            model = model + ".en"
        
        self.audio_model = whisper.load_model(model).to(device)

        self.audio_queue = queue.Queue()
        self.result_queue: "queue.Queue[str]" = queue.Queue()

        self.break_threads = False
        self.mic_active = False

        self.banned_results = [""," ","\n",None]

        self.setup_mic(mic_index)


    def setup_mic(self, mic_index):
        if mic_index is None:
            self.logger.info("No mic index provided, using default")
        self.source = sr.Microphone(sample_rate=16000, device_index=mic_index)

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.energy
        self.recorder.pause_threshold = self.pause
        self.recorder.dynamic_energy_threshold = self.dynamic_energy

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=2)
        self.logger.info("Mic setup complete, you can now talk")


    def preprocess(self, data):
        return torch.from_numpy(np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0)

    def get_all_audio(self, min_time: float = -1.):
        audio = bytes()
        got_audio = False
        time_start = time.time()
        while not got_audio or time.time() - time_start < min_time:
            while not self.audio_queue.empty():
                audio += self.audio_queue.get()
                got_audio = True

        data = sr.AudioData(audio,16000,2)
        data = data.get_raw_data()
        return data


    def record_callback(self,_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.audio_queue.put_nowait(data)


    def transcribe_forever(self) -> None:
        while True:
            if self.break_threads:
                break
            self.transcribe()


    def transcribe(self,data=None, realtime: bool = False) -> None:
        if data is None:
            audio_data = self.get_all_audio()
        else:
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

        if self.save_file:
            os.remove(audio_data)


    def listen_loop(self, dictate: bool = False) -> None:
        threading.Thread(target=self.transcribe_forever).start()
        while True:
            result = self.result_queue.get()
            print(result)


    def listen(self, timeout: int = 3):
        audio_data = self.get_all_audio(timeout)
        self.transcribe(data=audio_data)
        while True:
            if not self.result_queue.empty():
                return self.result_queue.get()

    def toggle_microphone(self) -> None:
        #TO DO: make this work
        self.mic_active = not self.mic_active
        if self.mic_active:
            print("Mic on")
        else:
            print("turning off mic")
            self.mic_thread.join()
            print("Mic off")


def test_tts(share_path, device):
   # List available 🐸TTS models and choose the first one
    model_name = TTS().list_models()[0]
    tts_root = Path("/home/oumuamua/.local/share/tts")
    # Init TTS
    tts = TTS(
        model_path           = Path(tts_root, "tts_models--en--ljspeech--glow-tts"),
        config_path          = Path(tts_root, "tts_models--en--ljspeech--glow-tts", "config.json"),
        vocoder_path         = Path(tts_root, "vocoder_models--de--thorsten--fullband-melgan"),
        vocoder_config_path   = Path(tts_root, "vocoder_models--de--thorsten--fullband-melgan", "config.json")
    ).to(device)

    # Run TTS
    # ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
    # Text to speech with a numpy output
    wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
    # Text to speech to a file
    tts.tts_to_file(
        text="Hello world!", 
        file_path=Path(share_path, "output.wav")
    )


def pyaudio_test():
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Record
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    print("Recording...")
    frames = []
    for i in range(0, int(p.get_device_info_by_index(1)['defaultSampleRate'] / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    print("Recording finished.")

    # Play
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    print("Playing back...")
    for frame in frames:
        stream.write(frame)
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

class TTSProcessor:
    def __init__(self, tts_root = "/home/oumuamua/.local/share/tts", cache_path = "/tmp", device = "cuda"):
        self.tts_root = Path(tts_root)
        self.cache_path = cache_path

        model_path           = Path(self.tts_root, "tts_models--en--ljspeech--glow-tts", "model_file.pth")
        config_path          = Path(self.tts_root, "tts_models--en--ljspeech--glow-tts", "config.json")
        vocoder_path         = Path(self.tts_root, "vocoder_models--en--ljspeech--multiband-melgan_glitch", "model_file.pth")
        _vocoder_config_path = Path(self.tts_root, "vocoder_models--en--ljspeech--multiband-melgan_glitch", "config.json")
        vocoder_config_path  = Path(self.tts_root, "vocoder_models--en--ljspeech--multiband-melgan_glitch", "_config.json")

        with open(_vocoder_config_path, 'r') as file:
            data = file.read()
        data = data.replace('/home/meredityman/', '/home/oumuamua/')
        with open(vocoder_config_path, 'w') as file:
            file.write(data)

        # Init TTS
        self.tts = TTS(
            model_path            = model_path         ,
            config_path           = config_path        ,
            vocoder_path          = vocoder_path       ,
            vocoder_config_path   = vocoder_config_path
        ).to(device)

        self.message_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self.process_queue)
        # self.processing_thread.start()

    def add_message(self, message):
        self.message_queue.put(message)


    def process_queue(self):
        while True:
            message= self.message_queue.get()
            self.process_message(message)
            
    def process_message(self, message):
        print(f"Processing message: {message}")
        wav_uuid = uuid.uuid4()
        wav_file_path = Path(self.cache_path, f"{wav_uuid}.wav")
        self.tts.tts_to_file(
            text=message, 
            file_path=Path(wav_file_path)
        )
        play_proc = subprocess.Popen(["aplay", wav_file_path])

    def stop(self):
        self.add_message("STOP")
        self.processing_thread.join()




def main():
    logging.info(f"Entering {__name__}...")
    logging.info(subprocess.call("nvidia-smi"))
    # logging.info(subprocess.call("pactl info"))
    # Get device

    share_path = Path("share")

    assert(torch.cuda.is_available())
    device = "cuda"

    # test_tts(share_path, device)
    # pyaudio_test()



    with noalsaerr():
        mic_index = sr.Microphone.list_microphone_names().index("pulse")
        mic = WhisperMic(mic_index=mic_index)


    processor = TTSProcessor(cache_path = share_path)
    # processor.add_message("Hello, World!")
    # processor.add_message("How are you?")

    while(True):
        try:
            logging.info("Listening...")
            result = mic.listen(timeout=4)
            result = result.encode('ascii','ignore').decode("ascii").strip()
            if result == "":
                continue

            logging.info(f"Result: {result}")
            processor.process_message(result)
        finally:
            pass
            # processor.stop()




if __name__ == "__main__":
    main()