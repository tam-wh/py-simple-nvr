FROM python:3.9.5-slim-buster
LABEL maintainer="tam-wh"

ENV FFMPEG_URL  https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

RUN apt-get update && apt-get install -y --no-install-recommends wget xz-utils \
    && mkdir -p /tmp/ffmpeg \
    && cd /tmp/ffmpeg \
    && wget -O ffmpeg.tar.xz "$FFMPEG_URL" \
    && tar -xf ffmpeg.tar.xz -C . --strip-components 1 \
    && cp ffmpeg ffprobe qt-faststart /usr/bin \
    && cd .. \
    && rm -fr /tmp/ffmpeg \
    && apt-get purge -y --auto-remove wget xz-utils \
    && rm -fr /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade paho-mqtt pyyaml flask

RUN mkdir app
WORKDIR /app
COPY . /app


CMD [ "python", "./__main__.py" ]