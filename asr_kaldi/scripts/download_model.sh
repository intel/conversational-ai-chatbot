#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

model_path=''
config_file=''
while getopts 'c:d:' flag; do
  case "${flag}" in
    c) config_file="${OPTARG}" ;;
    d) model_path="${OPTARG}" ;;
    v) verbose='true' ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

function usage() {
  echo "usage: $0 -c <config.yml> -d <output_dir>"
}

function create_venv() {
  venv_dir=$1
  mkdir -p ${venv_dir}
  python3 -m venv ${venv_dir}
  source ${venv_dir}/bin/activate
}

function cleanup_venv() {
  venv_dir=$1
  deactivate
  rm -rf ${venv_dir}
}

function download_model() {
  config=$1
  install_dir=$2
  echo "Download openmodel zoo"
  mkdir -p ${install_dir}
  #Download model from location
  wget https://github.com/openvinotoolkit/open_model_zoo/archive/refs/tags/2019_R3.1.zip \
	    && unzip 2019_R3.1.zip

  python3 -m pip install -r open_model_zoo-2019_R3.1/tools/downloader/requirements.in
  python3 open_model_zoo-2019_R3.1/tools/downloader/downloader.py -c $config -o ${install_dir} --all
  rm -rf  2019_R3.1.zip
  rm -rf open_model_zoo-2019_R3.1
}

# Main program starts here
[[ ! -f ${config_file} ]] && usage && exit 0
venv_path='tmp/venv'
echo "Download KALDI Model optimised for inference engine"
echo "download using [${config_file}] to dir: [${model_path}]"
create_venv ${venv_path}
download_model ${config_file} ${model_path}
cleanup_venv ${venv_path}
