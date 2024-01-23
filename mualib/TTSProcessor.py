import logging, time, queue, threading, uuid, subprocess
from pathlib import Path
import openai
from mualib.TTSUtils import load_tts_model

logger = logging.getLogger()

openai.api_key = open("/home/oumuamua/openai.key").read()

class TTSProcessor:
    def __init__(self, script, system_prompt, tts_root = "/home/oumuamua/.local/share/tts", cache_path = "/tmp", device = "cuda"):
        self.system_prompt = system_prompt
        self.tts_root = Path(tts_root)
        self.cache_path = cache_path
        self.device = device
        self.tts    = None
        self.vocoder_model = "vocoder_models--en--ljspeech--multiband-melgan"
        self.loaded_model  = None
        self.desired_model = None
        self.script_line = None

        self.reset(script)

        self.file_lock = threading.Lock()
        self.ready_files = []

        self.message_queue  = queue.Queue()
        self.response_queue = queue.Queue()

    def start(self):
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_queue)
        self.processing_thread.start()

    def reset(self, script):
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
        # Init TTS
        self.tts = load_tts_model(model, self.vocoder_model, self.tts_root, self.device)
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
    def play_audio(self, wav_files, blocking=True):
        wav_files = [str(f.resolve()) for f in wav_files]
        logger.info(f"Playing: {', '.join(wav_files)}")
        play_proc = subprocess.Popen(["aplay"] + wav_files)
        if blocking:
            play_proc.communicate()

        logger.info("Finished Speaking")
            
    def process_message(self, message):

        self.history += [{"role": "user", "content": f'{message}'}]
        prompt = self.script_line["prompt"]

        return self.get_gpt_response(prompt)

    def get_gpt_response(self, prompt):
        for _ in range(5):
            try:
                messages = [{"role": "system", "content": self.system_prompt}]
                messages += [ m for m in self.history]
                messages += [ {"role": "system", "content": f'{prompt}'}]
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages)

                return response.choices[0].message.content
            except Exception as e:
                logging.warn(e)
                time.sleep(1.0)
        
        logging.warn("GPT Timed out!")
        return "I am lost"

    def speak(self, response_message):
        wav_uuid = uuid.uuid4()
        wav_file_path = Path(self.cache_path, f"{wav_uuid}.wav")
        logger.info(f"Processing message: '{response_message}' -> {wav_file_path}")
        # try:
        self.tts.tts_to_file(
            text=response_message, 
            file_path=Path(wav_file_path)
        )
        logger.info(f"Saved: {wav_file_path}")
        self.ready_files.append(wav_file_path)
        # except Exception as e:
        #     logger.error(e)

    def stop(self):
        self.running = False
        self.processing_thread.join()


