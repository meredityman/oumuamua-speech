#!/bin/sh

export DOCKER_BUILDKIT=1

set -eu


load_audio(){
    echo Loading Pulse Audio Module...
    sudo rm -fd /tmp/pulseaudio.client.conf
    sudo rm -fd /tmp/pulseaudio.socket
    PA_PID=$(pactl load-module module-native-protocol-unix socket=/tmp/pulseaudio.socket)
    cp -f pulseaudio.client.conf /tmp
}

setup_audio() {
    SUCCESS=$(pactl info 2>&1 &)
    # echo pactl returned: $SUCCESS
    if $(echo "$SUCCESS" | grep failure); then
        echo Restarting Pulseaudio...
        pulseaudio -v -k | /bin/true
        pulseaudio -v --start
    fi

    MODULES=$(pactl list modules short | grep socket=/tmp/pulseaudio.socket | wc -l)
    if [ $MODULES -eq 1 ]; then
        echo Found Socket
    elif [ $MODULES -gt 1 ]; then
        pactl unload-module module-native-protocol-unix
        load_audio
    else
        load_audio
    fi   
}

build() {
    docker build  --rm . --tag "oumuamua"
}

perturb() {
    docker run --rm --gpus=all --entrypoint=python3 \
        --network=host \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -it "oumuamua" perturb_model.py
}

make_audio() {
    docker run --rm --gpus=all --entrypoint=python3 \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -it oumuamua make_audio.py "$@"
}



dev() {
    setup_audio
    docker run --rm --gpus=all --entrypoint=bash \
        -p 3721:3721/udp \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        -v /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -v $HOME/.cache/whisper:/home/oumuamua/.cache/whisper \
        --user $(id -u):$(id -g) \
        -it "oumuamua"
        
}

speaker_test() {
    setup_audio
    docker run --rm --gpus=all --entrypoint=speaker-test \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        --volume $PWD/pulseaudio.client.conf:/etc/pulse/client.conf \
        -v $PWD/share:/home/oumuamua/share \
        --user $(id -u):$(id -g) \
        -it "oumuamua" -c 2 -l 1 -t wav
}

whisper_test() {
#     
    setup_audio
    docker run --rm --gpus=all --entrypoint=/bin/bash \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        -v $PWD/share:/home/oumuamua/share \
        --user $(id -u):$(id -g) \
        -it "oumuamua" -i "arecord -D pulse -f cd -t wav -d 5 -r 44100 -c 1 test.wav && aplay test.wav"
}

run() {
    setup_audio
    docker run --rm --gpus=all --device=/dev/snd \
        -p 3721:3721/udp \
        -e PYTHONUNBUFFERED=1 \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        --volume $PWD/pulseaudio.client.conf:/etc/pulse/client.conf \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -v $HOME/.cache/whisper:/home/oumuamua/.cache/whisper \
        "oumuamua" "$@"
}


CWD=$(basename "$PWD")

case ${1:-build} in
    build) build ;;
    dev) dev ;;
    perturb) perturb ;;
    make_audio) shift; make_audio "$@";;
    speaker_test) speaker_test ;;
    whisper_test) whisper_test ;;
    run) run ;;
    *) echo "$0: No command named '$1'" ;;
esac