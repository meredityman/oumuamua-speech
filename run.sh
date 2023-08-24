#!/bin/bash


# text="Lumix splendora, starran glimmerix,
# Zentara zorixa, glistens in the nix.
# Frollexian winds, wisp and weave,
# Nebula's dance, the cosmos conceive."
text="Important note, while iterable, a space separated list of words is not an array. Wrap it like so (a b c) to convert it to an array. "


tts_root=/home/meredityman/.local/share/tts
orig_model_root=$tts_root/tts_models--en--ljspeech--glow-tts
model_root=$tts_root/tts_models--en--ljspeech--glow-tts_glitch
vocoder_roots=( \
    # "$tts_root/vocoder_models--en--ljspeech--multiband-melgan" \
    # "$tts_root/vocoder_models--en--ljspeech--univnet" \
    # "$tts_root/vocoder_models--en--ljspeech--hifigan_v2" \
    "$tts_root/vocoder_models--de--thorsten--fullband-melgan" \
)


python3 perturb_model.py --input_path "$orig_model_root/model_file.pth" --output_path "$model_root/model_file.pth"

for i in "${!vocoder_roots[@]}"; do
    vocoder_path=${vocoder_roots[$i]}
    tts --text "$text" \
        --model_path "$orig_model_root/model_file.pth" \
        --config_path "$orig_model_root/config.json" \
        --vocoder_path  "$vocoder_path/model_file.pth" \
        --vocoder_config_path "$vocoder_path/config.json"  \
        --out_path "outputs/vov_${i}.wav" && aplay "outputs/vov_${i}.wav" 
done
# tts --use_cuda 1 --text "$text" \
#     --out_path outputs/speech.wav && aplay outputs/speech.wav     