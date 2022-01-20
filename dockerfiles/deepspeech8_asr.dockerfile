# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_data_dev:2021.3 as builder
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
# Installing dependencies to download openvino  models
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv wget unzip build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Downloading Opensource deepspeech models
USER openvino
COPY asr_deepspeech/scripts/download_model.sh /home/openvino/
RUN pip install wheel
RUN cd /home/openvino \
    && ./download_model.sh
RUN cd /home/openvino/tmp/model/python/ctcdecode-numpy  && python3 -m pip wheel .

FROM openvino/ubuntu18_runtime:2021.3

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
# copy the content of the local src directory to the working directory
COPY asr_deepspeech/src/model /model
COPY asr_deepspeech/requirements.txt /tmp/requirements.txt
RUN python3 -mpip install -r /tmp/requirements.txt
RUN apt-get update && apt-get install libsndfile1 -y

# copy downloaded models from the first stage
COPY --from=builder /home/openvino/tmp/model /demo
RUN cd /demo/python/ctcdecode-numpy  && python3 -m pip install *.whl
RUN cp -rf /demo/public /model/public && rm -rf /demo

COPY asr_deepspeech/src /app/src/
RUN cd /app/src && ./install.sh

# Install integration lib
COPY integration_library /tmp/integration_library
RUN cd /tmp/integration_library/zmq_integration_lib \
    && bash install.sh

COPY asr_deepspeech/run.sh /app/

COPY dockerfiles/create_user.sh /create_user.sh
RUN chmod a+x /create_user.sh \
     && /create_user.sh \
     && rm /create_user.sh \
     && usermod -aG audio sys-admin
USER sys-admin

CMD ["bash", "-c","/app/run.sh"]
