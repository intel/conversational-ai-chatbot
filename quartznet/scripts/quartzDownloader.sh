#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

echo "Download and convert quartz model  to openvino IR format"
mkdir -p tmp/venv
python3 -m venv tmp/venv
source tmp/venv/bin/activate
python3 -mpip install protobuf>=3.15.6
python3 -mpip install mxnet~=1.2.0

#python3 -mpip install mxnet~=1.7.0.post2
python3 -mpip install wheel numpy numpy tqdm numba==0.48.0 librosa==0.8.1 pyyaml networkx~=2.5 

#python3 -mpip install "numpy>=1.16.6,<1.20"
python3 -mpip install defusedxml>=0.7.1 requests>=2.25.1 tensorflow~=2.4.1 defusedxml>=0.7.1 urllib3>=1.26.4 requests>=2.25.1

python3 -m pip install --upgrade pip
python3 -mpip install onnx==1.9.0
python3 -mpip install torch==1.9.1 torchvision 

python3 -mpip install  wrapt
python3 -mpip install monotonic
python3 -mpip install netifaces

python3 -mpip install defusedxml
# source openvino
source /opt/intel/openvino/bin/setupvars.sh

echo "Download openmodel zoo"
mkdir -p tmp/model
#Download model from location
cd tmp && wget https://github.com/openvinotoolkit/open_model_zoo/archive/refs/tags/2021.4.zip \
	    && unzip 2021.4.zip && cd -

cp -rf tmp/open_model_zoo-2021.4/demos/speech_recognition_quartznet_demo/python tmp/model

echo "Downloading quartznet-15x5-en"
cd tmp/model \
   && python3 ../open_model_zoo-2021.4/tools/downloader/downloader.py --name quartznet-15x5-en \
   && cd -

echo "Converting quartznet to openvino IR format"
source /opt/intel/openvino_2021/bin/setupvars.sh
python3 -m pip install -r /opt/intel/openvino_2021/deployment_tools/model_optimizer/requirements_onnx.txt
python3 -m pip uninstall  termcolor -y
python3 -m pip install  termcolor

cd tmp/model \
    && python3 ../open_model_zoo-2021.4/tools/downloader/converter.py --name quartznet-15x5-en  \
    && cd -

mkdir -p  Models
cp /home/openvino/tmp/model/public/quartznet-15x5-en/FP32/quartznet-15x5-en.* Models/.


#echo " Run Inference Engine"
#cd /opt/intel/openvino_2021/deployment_tools/open_model_zoo && python3 ./demos/speech_recognition_quartznet_demo/python/speech_recognition_quartznet_demo.py -m /home/openvino/tmp/model/public/quartznet-15x5-en/FP32/quartznet-15x5-en.xml -i ../demo/how_are_you_doing.wav && cd -
