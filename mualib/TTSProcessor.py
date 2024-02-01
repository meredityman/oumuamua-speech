import logging, time, queue, threading, uuid, subprocess, re
from pathlib import Path
import openai
from mualib.TTSUtils import load_tts_model

logger = logging.getLogger()

openai.api_key = open("/home/oumuamua/openai.key").read()

class TTSProcessor:
    def __init__(
            self, 
            model_list, 
            system_prompt, 
            default_lang = "en",
            tts_root     = "/home/oumuamua/.local/share/tts", 
            cache_path   = "/tmp", 
            device       = "cuda"
            ):
        
        self.orig_model_list = model_list
        self.system_prompt   = system_prompt
        self.default_lang    = default_lang 
        self.tts_root        = Path(tts_root)
        self.cache_path      = cache_path
        self.device          = device


        self.tts    = {}
        # self.vocoder_model = "vocoder_models--en--ljspeech--multiband-melgan"
        self.model_list_line   = None

        self.load_models()
        self.reset()

        self.file_lock   = threading.Lock()
        self.ready_files = []

        self.message_queue  = queue.Queue()
        self.response_queue = queue.Queue()

    def start(self):
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_queue)
        self.processing_thread.start()

    def reset(self):
        self.history = []
        self.model_list = self.orig_model_list.copy()
        self.model_list_line   = self.model_list[0]

    def iterate(self):
        self.model_list_line   = self.model_list.pop(0)
        if(len(self.model_list) == 0):
            logger.warning("Finished model_list")
            self.reset()


    def load_models(self):
        self.tts = {}
        # Init TTS

        for line in self.orig_model_list:
            model = line["en"]["model"]
            if(model not in self.tts):
                self.tts[model] = load_tts_model(model, None, self.tts_root, self.device)

            model = line["de"]["model"]
            if(model not in self.tts):
                self.tts[model] = load_tts_model(model, None, self.tts_root, self.device)


    def add_message(self, message, role, lang):
        self.file_lock.acquire()
        if(role == "user"):
            self.message_queue.put(message)
        elif(role == "assistant"):
            self.response_queue.put((message, lang))

    def play_all_audio(self, timeout=-1):
        if self.file_lock.acquire(blocking=True, timeout=timeout):
            files, self.ready_files = self.ready_files, []
            self.file_lock.release()
            self.play_audio(files)

    def process_queue(self):
        while self.running:
            try:
                message = self.message_queue.get(timeout=0.1)
                if(message):
                    (response_message, lang) = self.process_message(message)
                    self.response_queue.put_nowait((response_message, lang))
            except queue.Empty:
                # logging.warn("Message timeout")
                pass

            try:
                response_message, lang = self.response_queue.get(timeout=0.1)
                if(response_message):
                    self.speak(response_message, lang)
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
        prompt = self.model_list_line[self.default_lang ]["prompt"]
        resp = self.get_gpt_response(prompt)
        resp, lang = TTSProcessor.get_lang(resp, self.default_lang )
        return resp, lang
    

    def get_lang(resp, default_lang):
        pattern = r'\b(?:\[)?(English|German)\]?\b'
        matches = re.findall(pattern, resp, re.IGNORECASE)
        if(len(matches)):
            logging.info(f"Matches: {matches}")
            pattern = r'\s*\[?(English|German)\]?\s*'  
            if(matches[0] == "English"):
                lang = "en"   
                resp = re.sub(pattern, "", resp, flags=re.IGNORECASE).strip()
            elif(matches[0] == "German"):
                lang = "de"   
                resp = re.sub(pattern, "", resp, flags=re.IGNORECASE).strip()
            else:
                logging.error(matches)
                lang = default_lang
        else:
            logging.warn(f"No language found {resp}")
            lang = default_lang

        return resp, lang

    def get_gpt_response(self, prompt):
        for _ in range(5):
            try:
                messages = [{"role": "system", "content": self.system_prompt}]
                messages += [ m for m in self.history]
                messages += [ {"role": "system", "content": f'{prompt}'}]

                logging.info(f"GPT Complete: {messages}")
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    frequency_penalty=1.0,
                    max_tokens=150
                )
                resp = response.choices[0].message.content
                logging.info(f"Reponse: {resp}")
                return resp
            except Exception as e:
                logging.warn(e)
                time.sleep(1.0)
        
        logging.warn("GPT Timed out!")
        return "I am lost"

    def speak(self, response_message, lang):
        wav_uuid = uuid.uuid4()
        wav_file_path = Path(self.cache_path, f"{wav_uuid}.wav")
        logger.info(f"Processing message: '{response_message}' -> {wav_file_path}")
        try:
            model = self.model_list_line[lang]["model"]
            self.tts[model].tts_to_file(
                text=response_message, 
                file_path=Path(wav_file_path)
            )
            logger.info(f"Saved: {wav_file_path} using model: {model}")
            self.ready_files.append(wav_file_path)
        except Exception as e:
            logger.error(e)
        
        self.file_lock.release()

    def stop(self):
        self.running = False
        self.processing_thread.join()


