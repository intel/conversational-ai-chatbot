#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

echo "Download and convert deepspeech model  to openvino IR format"

mkdir -p tmp/venv
python3 -m venv tmp/venv
source tmp/venv/bin/activate
python3 -m pip install --upgrade pip
python3 -mpip install wheel numpy numpy tqdm numba==0.49.0 librosa pyyaml

# source openvino
source /opt/intel/openvino/bin/setupvars.sh

echo "Download openmodel zoo"
mkdir -p tmp/model
#Download model from location
cd tmp && wget https://github.com/openvinotoolkit/open_model_zoo/archive/refs/tags/2021.3.zip \
	    && unzip 2021.3.zip && cd -

cp -rf tmp/open_model_zoo-2021.3/demos/speech_recognition_demo/python tmp/model

echo "Downloading deepspeech-0.8.2"
cd tmp/model \
   && python3 ../open_model_zoo-2021.3/tools/downloader/downloader.py --name mozilla-deepspeech-0.8.2 \
   && cd -

# convert (uses openvino)
#if openvino is there then convert
# source openvino
echo "Converting deepspeech to openvino IR format"
source /opt/intel/openvino/bin/setupvars.sh
python3 -m pip install -r /opt/intel/openvino/deployment_tools/model_optimizer/requirements_tf.txt
python3 -m pip uninstall  termcolor -y
python3 -m pip install  termcolor

cd tmp/model \
    && python3 ../open_model_zoo-2021.3/tools/downloader/converter.py --name mozilla-deepspeech-0.8.2 \
    && cd -

echo "Clean up temporary files"
# cleanup 
rm tmp/model/public/mozilla-deepspeech-0.8.2/deepspeech-0.8.2-models.pb* \
    && rm -rf tmp/model/public/mozilla-deepspeech-0.8.2/deepspeech-0.8.2-models.scorer \
    && rm -rf tmp/open_model_zoo-2021.3 \
    && rm tmp/2021.3.zip \
    && rm -rf tmp/venv

echo "Model is available at tmp/model/public"
