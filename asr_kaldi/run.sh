#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause


source /opt/intel/openvino/bin/setupvars.sh 
export PYTHONPATH=$PYTHONPATH:/speech_library
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/app/lib
cd /app/src && python3 main.py
