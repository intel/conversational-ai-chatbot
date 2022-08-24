# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM python:3.11.0rc1-slim-buster
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://deb.debian.org#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
WORKDIR /app
# copy the content of the local src directory to the working directory
COPY nlp/app/* /app/
# Installing requirements
RUN python3 -mpip install -r /app/requirements.txt

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
