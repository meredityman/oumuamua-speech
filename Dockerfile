ARG BASE=nvidia/cuda:11.8.0-base-ubuntu22.04
FROM ${BASE}
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
        alsa-base alsa-utils pulseaudio portaudio19-dev \
        gcc g++ make python3 python3-dev python3-pip python3-venv python3-wheel \
        espeak-ng libsndfile1-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*


RUN --mount=type=cache,target=/root/.cache \
    pip3 install pyaudio TTS openai-whisper SpeechRecognition 

# RUN rm -rf /root/.cache/pip

RUN useradd -m oumuamua

USER oumuamua

WORKDIR /home/oumuamua
RUN mkdir -p /home/oumuamua/.local/share/tts/
RUN mkdir -p /home/oumuamua/.cache/whisper/
RUN mkdir -p /home/oumuamua/share
# COPY . /root

COPY entrypoint.py /home/oumuamua

CMD ["entrypoint.py"]
ENTRYPOINT ["python3"]