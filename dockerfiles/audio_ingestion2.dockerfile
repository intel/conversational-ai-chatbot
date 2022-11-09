# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM ubuntu:18.04
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
RUN mkdir /app
COPY audio_ingestion2/requirements.txt /app/

WORKDIR /app

RUN apt update -y \
    && apt  install -y  python3-pip swig git libpulse-dev libasound2-dev python3-pyaudio
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

# Downloading Respeaker SDK
RUN git clone https://github.com/respeaker/respeaker_python_library.git
COPY audio_ingestion2/_config.py respeaker_python_library/examples/_config.py
COPY audio_ingestion2/main.py respeaker_python_library/examples/main.py
COPY audio_ingestion2/dictionary.txt respeaker_python_library/respeaker/pocketsphinx-data/dictionary.txt
COPY audio_ingestion2/keywords.txt respeaker_python_library/respeaker/pocketsphinx-data/keywords.txt
COPY audio_ingestion2/run.sh .

# Install integration lib
COPY integration_library /tmp/integration_library
RUN cd /tmp/integration_library/zmq_integration_lib \
    && bash install.sh

COPY dockerfiles/create_user.sh /create_user.sh
RUN chmod a+x /create_user.sh \
     && /create_user.sh \
     && rm /create_user.sh \
     && usermod -aG audio sys-admin
USER sys-admin
