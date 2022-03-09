# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM openvino/ubuntu18_dev:2021.4 as builder
LABEL maintainer Vinay <vinay.g@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
# copy the content of the local src directory to the working directory
COPY quartznet /app/

# Installing dependencies
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv wget --no-install-recommends \
    && apt-get install -y unzip \
    && apt-get install -y protobuf-compiler libprotobuf-dev \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*


USER openvino
# Download open source quartznet model
COPY quartznet/scripts/quartzDownloader.sh /home/openvino/
RUN cd /home/openvino \
    && ./quartzDownloader.sh && cd -

FROM openvino/ubuntu18_runtime:2021.4

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL

# Copy from first stage
USER root
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://.*archive.ubuntu.com#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
COPY --from=builder /home/openvino/Models /Models
COPY --from=builder /app /app


RUN pip install -r /app/requirements.txt

# Installing ZMQ wrapper
COPY integration_library /app/src//integration_library
RUN cd /app/src/integration_library/zmq_integration_lib \
    && bash install.sh
COPY dockerfiles/create_user.sh /create_user.sh
RUN chmod a+x /create_user.sh \
     && /create_user.sh \
     && rm /create_user.sh \
     && usermod -aG audio sys-admin

RUN chmod a+x /app/run.sh

USER sys-admin

CMD ["bash", "-c","/app/run.sh"]
