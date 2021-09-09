# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_dev:2020.4 as builder
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

USER root
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv wget --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* 

USER openvino
COPY asr_deepspeech/scripts/download_model.sh /home/openvino/
RUN cd /home/openvino \
    && ./download_model.sh

FROM openvino/ubuntu18_runtime:2020.4
USER root

COPY asr_deepspeech/src/model /model
COPY asr_deepspeech/requirements.txt /tmp/requirements.txt
RUN python3 -mpip install -r /tmp/requirements.txt 
COPY --from=builder /home/openvino/tmp/model /demo
RUN cd /demo/python/ctcdecode-numpy  && python3 -m pip install .
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

