#!/bin/sh

export DOCKER_BUILDKIT=1

set -eu


setup_audio() {
    SUCCESS=$(pactl info 2>&1 &)
    # echo pactl returned: $SUCCESS
    if $(echo "$SUCCESS" | grep failure); then
        echo Restarting Pulseaudio...
        pulseaudio -v -k | /bin/true
        pulseaudio -v --start
    fi

    # if $(pactl list modules short | grep socket=/tmp/pulseaudio.socket); then
    #     echo Found Socket
    # else
    #     echo Loading Pulse Audio Module...
    #     sudo rm -fd /tmp/pulseaudio.socket
    #     PA_PID=$(pactl load-module module-native-protocol-unix socket=/tmp/pulseaudio.socket)
    #     cp -f pulseaudio.client.conf /tmp
    # fi   
}

build() {
    docker build  --rm . --tag "oumuamua"
}

dev() {
    setup_audio
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
    setup_audio
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
#     arecord -D pulse -f cd -t wav -d 5 -r 44100 -c 1 test.wav && aplay test.wav
    setup_audio
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
    setup_audio
    docker run --rm --gpus=all --device=/dev/snd \
        -e PYTHONUNBUFFERED=1 \
        --env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
        --env PULSE_COOKIE=/tmp/pulseaudio.cookie \
        --volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
        --volume /tmp/pulseaudio.client.conf:/etc/pulse/client.conf \
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