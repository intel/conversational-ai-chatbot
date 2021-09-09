# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_dev:2020.4 as builder

USER root
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv wget --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* 

USER openvino
COPY scripts/download_model.sh /home/openvino/
RUN cd /home/openvino \
    && ./download_model.sh

FROM openvino/ubuntu18_dev:2020.4
USER root
RUN python3 -mpip install wheel numpy tqdm numba==0.49.0 librosa pyyaml

ADD asr_deepspeech/src/model /model

COPY --from=builder /home/openvino/tmp/model /demo  
RUN cd /demo/python/ctcdecode-numpy  && python3 -m pip install .
RUN cp -rf /demo/public /model/public && rm -rf /demo

ADD asr_deepspeech/src /app/src/

# Install integration lib
COPY integration_library /tmp/integration_library
RUN cd /tmp/integration_library/zmq_integration_lib \
    && bash install.sh 

ADD asr_deepspeech/run.sh /app/

CMD ["bash", "-c","/app/run.sh"]

