ARG BASE=nvidia/cuda:11.8.0-base-ubuntu22.04
FROM ${BASE}
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
        alsa-base alsa-utils pulseaudio portaudio19-dev \
        gcc g++ make python3 python3-dev python3-pip python3-venv python3-wheel \
        espeak-ng libsndfile1-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*


RUN --mount=type=cache,target=/root/.cache \
    pip3 install pyaudio TTS openai-whisper SpeechRecognition openai==0.28

# RUN rm -rf /root/.cache/pip

RUN useradd -m oumuamua

USER oumuamua

WORKDIR /home/oumuamua
RUN mkdir -p /home/oumuamua/.local/share/tts/
RUN mkdir -p /home/oumuamua/.cache/whisper/
RUN mkdir -p /home/oumuamua/share
RUN mkdir -p /home/oumuamua/mualib
# COPY . /root

COPY pulseaudio.client.conf /etc/pulse/client.conf
COPY alsa.conf /usr/share/alsa/alsa.confs
COPY asoundrc /usr/etc/asound.confs

COPY make_audio.py    /home/oumuamua
COPY perturb_model.py /home/oumuamua
COPY entrypoint.py    /home/oumuamua
COPY openai.key       /home/oumuamua

ADD mualib        /home/oumuamua/mualib
ENV PYTHONPATH "${PYTHONPATH}:/home/oumuamua/mualib"

CMD ["entrypoint.py"]
ENTRYPOINT ["python3"]