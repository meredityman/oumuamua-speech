
import logging
from TTS.api import TTS
from pathlib import Path

logger = logging.getLogger()

def load_tts_model(model_name, vocoder_model, tts_root, device):
    # model = self.script_line["model"]
    # logger.info(str(TTS().list_models()))

    try:
        model_path           = Path(tts_root, model_name, "model_file.pth")
        assert(model_path.exists())
    except:
        logging.error(f"Can't find {model_path}")
        raise

    config_path          = Path(tts_root, model_name, "config.json")
    assert(config_path.exists())
    vocoder_path         = Path(tts_root, vocoder_model, "model_file.pth")
    assert(vocoder_path.exists())
    _vocoder_config_path = Path(tts_root, vocoder_model, "config.json")
    vocoder_config_path  = Path(tts_root, vocoder_model, "_config.json")


    logger.info(f"Loading model {model_name}")

    with open(_vocoder_config_path, 'r') as file:
        data = file.read()
    data = data.replace('/home/meredityman/', '/home/oumuamua/')
    with open(vocoder_config_path, 'w') as file:
        file.write(data)

    assert(vocoder_config_path.exists())   

    # Init TTS
    tts = TTS(
        model_name            = None,
        model_path            = model_path         ,
        config_path           = config_path        ,
        vocoder_path          = vocoder_path       ,
        vocoder_config_path   = vocoder_config_path,
    ).to(device)
    # tts.is_multi_lingual = False

    return tts 
