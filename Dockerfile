FROM python:3.9.5-slim-buster
LABEL maintainer="tam-wh"

VOLUME /config

RUN mkdir app
WORKDIR /app
COPY . /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    ffmpeg \
    libva-drm2 libva2 libmfx1 i965-va-driver vainfo intel-media-va-driver mesa-va-drivers \
    && rm -rf /var/lib/apt/lists/* \
    && (apt-get autoremove -y; apt-get autoclean -y)

RUN pip3 install --no-cache-dir --upgrade paho-mqtt pyyaml

CMD [ "python", "./__main__.py" ]