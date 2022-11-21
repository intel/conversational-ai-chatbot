# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

# set base image (host OS)
FROM python:3.10-slim-buster
LABEL maintainer Vinay <vinay.g@intel.com>

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR_URL
RUN [ ! -z "${APT_MIRROR_URL}" ] && sed -i -e "s#http://deb.debian.org#${APT_MIRROR_URL}#g" /etc/apt/sources.list || echo "APT_MIRROR_URL is not set"
# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY huggingface_asr/requirements.txt .

# install dependencies
RUN apt-get update -y && apt-get install libsndfile1 -y
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY  huggingface_asr/ .

COPY integration_library /tmp/integration_library
RUN cd /tmp/integration_library/zmq_integration_lib \
    && bash install.sh

COPY dockerfiles/create_user.sh /create_user.sh
RUN chmod a+x /create_user.sh \
     && /create_user.sh \
     && rm /create_user.sh \
     && usermod -aG audio sys-admin
USER sys-admin

# command to run on container start
CMD [ "python", "./hg.py" ]
