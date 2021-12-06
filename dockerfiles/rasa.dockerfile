# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM python:3.6-slim-buster
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

# Creating Rasa base image 
RUN mkdir -p /app
COPY nlp/rasa_actions_server/requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt


