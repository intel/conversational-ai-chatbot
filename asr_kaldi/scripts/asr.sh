#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

input_path=''
config_file=''
while getopts 'c:i:' flag; do
  case "${flag}" in
    c) config_file="${OPTARG}" ;;
    i) input_path="${OPTARG}" ;;
    v) verbose='true' ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

function usage() {
  echo "usage: ${0} -c <config.yml> -i <input.wav>"        
}


[[ ! -f ${config_file} ]] && usage && exit -1
[[ ! -f ${input_path} ]] && usage && exit -1

source /opt/intel/openvino/bin/setupvars.sh 
export PYTHONPATH=$PYTHONPATH:/speech_library
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/app/lib

cd /app/src && python3 cli.py -c ${config_file} -i ${input_path} 
