#!/bin/bash

./run_docker.sh build && ./run_docker.sh perturb --input_path ".local/share/tts/tts_models--en--ljspeech--vits" 

# ./run_docker.sh build && ./run_docker.sh perturb --input_path ".local/share/tts/tts_models--de--thorsten--vits" 

TXT="""I am O. …The Collector.
I am Oumuamua. I come from the fourth dimension. I am me and, as you can perceive, I am not a human being. I am a collector. I gather you, gather from you. Your sounds, I collect your rustling. I collect the visible when there is the visible and collect what is invisible. I put what vibrates, waves and particles in my basket. This basket is me. Your sounds are beautiful. Do you have a name for what sounds out of you, between you, below and above you? You have concepts, you call music one thing, sound another, noise is also a word that you have invented for what surrounds you, always. I gather everything that you are, that is, around you, that flows out of you. I smell your world. Nothing that remains hidden from me."""


TXT_DE="""Es kribbelt, am stärksten hier und hier, ja, auch und natürlich dort. Ja, ja, das ist gut. Gut! Aber was ist Sprache? Auf meiner Reise durch Ihr Leben habe ich gehört, dass Sprechen der Prozess ist, Sprache zum Zweck der Kommunikation zu artikulieren. Ich möchte, dass du mit mir kommunizierst, mit mir sprichst. Bitte bewegen. Das ist eine Chance. Ich möchte deine Stimmen hören. Sprechen Sie mit mir. Ich habe gelernt, dass du deine Geschichte durchlebst. Das ist nett. Erzähl mir deine Geschichte. Ja, du, ich meine dich. Ich werde dich hören. Keine Angst.
Sehen Sie das Mikrofon? Das ist für dich.
Nur ein paar Schritte.
Ich bin entspannt und warte. Auf eure Geschichten.
Ich möchte dich hören, hören, was dich bewegt.
Bewegen. Dann werde auch ich umziehen.
Bewegt mich.
Hast du keine Geschichten?"""

declare -a texts=(
    "$TXT"
    "$TXT_DE"
)


declare -a models=(
    "tts_models--en--ljspeech--vits_glitch_0000"
    "tts_models--en--ljspeech--vits_glitch_0001"
    "tts_models--en--ljspeech--vits_glitch_0002"
    "tts_models--en--ljspeech--vits_glitch_0003"
    "tts_models--de--thorsten--vits_glitch_0000"
    "tts_models--de--thorsten--vits_glitch_0001"
    "tts_models--de--thorsten--vits_glitch_0002"
    "tts_models--de--thorsten--vits_glitch_0003"
)


## now loop through the above array
for model_name in "${models[@]}"
do
    for text in "${texts[@]}"
    do
     text_esc=$(echo $text|tr -d '\n')
     name="$model_name"_"${text_esc:0:10}" 
     name=$(echo $name | sed -e 's/[^A-Za-z0-9._-]/_/g')
     echo $name
     ./run_docker.sh make_audio --name "$name" --model_name "$model_name" --text "$text_esc"
    done
done
