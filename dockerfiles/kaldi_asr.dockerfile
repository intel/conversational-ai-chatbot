# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_data_dev:2021.3 AS builder
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"

RUN mkdir -p /app/lib

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv wget unzip\
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Download models
COPY asr_kaldi/src/model /model
COPY asr_kaldi/scripts /scripts
RUN /scripts/download_model.sh -c /model/lspeech_s5_ext.yml -d /model

# Build speech processing library
RUN bash /opt/intel/openvino/data_processing/audio/speech_recognition/build_gcc.sh
RUN cp /opt/intel/openvino/data_processing/audio/speech_recognition/lib/x64/* /app/lib/
RUN cp /root/data_processing_demos_build/audio/speech_recognition/intel64/Release/lib/* /app/lib/

# copy the content of the local src directory to the working directory
COPY asr_kaldi/src /app/src/
COPY asr_kaldi/run.sh /app/
COPY asr_kaldi/scripts/asr.sh /app


FROM openvino/ubuntu18_runtime:2021.3

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

# Copy from first stage
USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
COPY --from=builder /app /app
COPY --from=builder /model /model
COPY --from=builder /opt/intel/openvino/data_processing/audio/speech_recognition/demos/live_speech_recognition_demo /speech_library


RUN apt-get update && apt-get install -y python3 python3-pip \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Installing dependencies
COPY asr_kaldi/requirements.txt /tmp/requirements.txt
RUN cd /tmp  && python3 -mpip install -r requirements.txt
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

CMD ["/app/run.sh"]
