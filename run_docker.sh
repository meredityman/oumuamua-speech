#!/bin/sh

export DOCKER_BUILDKIT=1

set -eu


setup_audio() {
    # echo Unloading...
    # pactl unload-module module-native-protocol-unix
    echo Loading Pulse Audio ModuleW...
    pactl load-module module-native-protocol-unix socket=/tmp/pulseaudio.socket
    cp -f pulseaudio.client.conf /tmp
    
}

build() {
    docker build  --rm . --tag "oumuamua"
}

dev() {
    docker run --rm --gpus=all --entrypoint=bash \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        -v /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        -v /tmp/pulseaudio.client.conf:/etc/pulse/client.conf \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -v $HOME/.cache/whisper:/home/oumuamua/.cache/whisper \
        --user $(id -u):$(id -g) \
        -it "oumuamua"
        
}

speaker_test() {
    docker run --rm --gpus=all --entrypoint=speaker-test \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        --volume /tmp/pulseaudio.client.conf:/etc/pulse/client.conf \
        -v $PWD/share:/home/oumuamua/share \
        --user $(id -u):$(id -g) \
        -it "oumuamua" -c 2 -l 1 -t wav
}

whisper_test() {
    docker run --rm --gpus=all --entrypoint=whisper_mic \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        --volume /tmp/pulseaudio.client.conf:/etc/pulse/client.conf \
        -v $PWD/share:/home/oumuamua/share \
        --user $(id -u):$(id -g) \
        -it "oumuamua" --loop --dictate
}

run() {
    echo "Running..."
    docker run --rm --gpus=all --device=/dev/snd \
        -e PYTHONUNBUFFERED=1 \
        -v $PWD/share:/home/oumuamua/share \
        -v $HOME/.local/share/tts:/home/oumuamua/.local/share/tts \
        -v $HOME/.cache/whisper:/home/oumuamua/.cache/whisper \
        "oumuamua" "$@"
}


CWD=$(basename "$PWD")

case ${1:-build} in
    build) build ;;
    dev) dev ;;
    speaker_test) speaker_test ;;
    whisper_test) whisper_test ;;
    run) run ;;
    *) echo "$0: No command named '$1'" ;;
esac