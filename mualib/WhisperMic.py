import logging, time, platform, queue
import torch
import whisper
import speech_recognition as sr
import numpy as np

logger = logging.getLogger()

class WhisperMic:
    def __init__(self,model="base",device=("cuda" if torch.cuda.is_available() else "cpu"),english=False,verbose=False,energy=300,pause=1.8,dynamic_energy=False,mic_index=None):
        # self.logger = get_logger("whisper_mic", "info")
        self.logger = logger
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.verbose = verbose
        self.english = english
        self.phrase_time_limit = 3
        # self.keyboard = pynput.keyboard.Controller()

        self.platform = platform.system()

        if (model != "large" and model != "large-v2") and self.english:
            model = model + ".en"
        

        logger.info("Loading Whisper...")
        self.audio_model = whisper.load_model(model).to(device)

        self.result_queue: "queue.Queue[str]" = queue.Queue()

        self.mic_active  = False
        self.audio_queue = None

        self.banned_results = [""," ","\n", "Thank you.", None]

        logger.info("Setting up Mic...")
        self.setup_mic(mic_index)


    def setup_mic(self, mic_index):
        if mic_index is None:
            self.logger.info("No mic index provided, using default")

        self.mic_index = mic_index

        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = self.energy
        self.recorder.pause_threshold  = self.pause
        self.recorder.dynamic_energy_threshold = self.dynamic_energy
        self.stop_callback = None


    def start_listening(self):
        
        if self.mic_active:
            raise

        self.audio_queue = queue.Queue()

        for _ in range(5):
            try:
                self.source = sr.Microphone(sample_rate=16000, device_index=self.mic_index)
                with self.source:
                    self.recorder.adjust_for_ambient_noise(self.source)
                break
            except AssertionError:
                time.sleep(0.2)

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
                    return self.result_queue.get(block=True, timeout=0.5).strip()
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
        while not got_audio or time.time() - time_start < 2.0:
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
