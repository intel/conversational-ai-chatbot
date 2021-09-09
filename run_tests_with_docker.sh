#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause


echo "Run Unit Tests for obp-api"
docker run --rm --name unittest -v $(pwd):/data  -it action_server:1.0 bash -c "cd /data/nlp/obp_api/test && python3 -m unittest discover -v"

echo "Run Unit Tests for Deepspeech ASR"
docker run --rm --name unittest -v $(pwd):/data  -it deepspeech_asr:1.0 bash -c "source /opt/intel/openvino/bin/setupvars.sh; \
cd /data/asr_deepspeech/src/asr/test/ && python3 -m unittest discover -v; \
cd /data/asr_deepspeech/src/deepspeech_openvino/test/ && python3 -m unittest discover -v;
cd /data/asr_deepspeech/src/speech_library/test/ && python3 -m unittest discover -v;"

echo "Run Unit Tests for Audio Ingestion"
docker run --rm --name unittest -v $(pwd):/data  -it audio-ingester:1.0 bash -c "cd /data/audio_ingestion/src/test && python3 -m unittest discover -v"

echo "Run Unit Tests for Audio Ingestion 2"

echo "Run Unit Tests for TTS"
docker run --rm --name unittest -v $(pwd):/data  -it deepspeech_asr:1.0 bash -c "source /opt/intel/openvino/bin/setupvars.sh; \
cd /data/tts/test/ && python3 -m unittest discover -v;"

echo "Run Unit Tests for authz"
docker run --rm --name unittest -v $(pwd):/data  -it authz:1.0 bash -c "cd /data/authz/test/ && python3 -m unittest discover -v;"

echo "Run Unit Tests for integration lib"
docker run --rm --name unittest -v $(pwd):/data  -it authz:1.0 bash -c "cd /data/integration_library/zmq_integration_lib/test/ && python3 -m unittest discover -v;"
