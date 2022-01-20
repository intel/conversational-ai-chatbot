# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_data_dev:2021.3 as builder
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL=""

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"

RUN apt-get update \
    && apt-get install -y python3-pip wget zip python3-dev libasound2-dev

# Download TTS open source models
COPY tts/tts_openvino /tmp/tts_openvino
RUN cd /tmp/tts_openvino && ./prepare_and_install.sh download

RUN cd /opt/intel/openvino_2021.3.394/deployment_tools/tools/model_downloader && python3 downloader.py --print_all | grep text-to-speech > models.lst
RUN cd /opt/intel/openvino_2021.3.394/deployment_tools/tools/model_downloader && python3 downloader.py --list models.lst --precisions FP32 -j 4
RUN mkdir -p /model
WORKDIR /opt/intel/openvino_2021.3.394/deployment_tools/tools/model_downloader
RUN cp intel/text-to-speech-en-0001/text-to-speech-en-0001-regression/FP32/* /model/ \
    &&  cp intel/text-to-speech-en-0001/text-to-speech-en-0001-generation/FP32/* /model/. \
		    && cp intel/text-to-speech-en-0001/text-to-speech-en-0001-duration-prediction/FP32/* /model/.

# build wheel here and copy to next stage
RUN cd /tmp && python3 -m pip wheel simpleaudio

FROM openvino/ubuntu18_runtime:2021.3

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"

COPY --from=builder /model /model
COPY --from=builder /tmp/tts_openvino /tmp/tts_openvino
COPY --from=builder /tmp/*.whl /tmp/

RUN apt-get update \
    && apt-get install -y python3-pip libasound2

RUN cd /tmp/tts_openvino \
    && ./prepare_and_install.sh install \
    && ./prepare_and_install.sh clean

WORKDIR /app
COPY tts/src/* /app/
COPY tts/requirements.txt /tmp/requirements.txt
# install simpleaudio from wheel
RUN python3 -mpip install  /tmp/*.whl
RUN python3 -mpip install -r /tmp/requirements.txt
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
