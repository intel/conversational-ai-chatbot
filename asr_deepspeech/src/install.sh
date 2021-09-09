#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

# Check and install dependancies
# ctcdecode-numpy is downloaded from openmodel zoo
package_to_check=ctcdecode_numpy
check_for_package=$(python3 -c "import ${package_to_check}" 2>&1| grep ModuleNotFoundError | wc -l)
[[ ${check_for_package} -gt 0 ]] && echo "${package_to_check} not found." && exit 0

# Install local packages
packages_to_install="deepspeech_openvino asr speech_library"
for package in $packages_to_install
do
   echo "Installing $package"
   #cd $package  && python3 setup.py install && cd -
   cd $package  && python3 -mpip install . && cd -
done

function download_and_install_ctcdecode_numpy() {
    mkdir tmp
    # Download model from location
    cd tmp && wget https://github.com/openvinotoolkit/open_model_zoo/archive/refs/tags/2021.3.zip \
       && unzip 2021.3.zip && cd -
    cd tmp/open_model_zoo-2021.3/demos/speech_recognition_demo/python/ctcdecode-numpy  \
       && python3 -m pip install .
    rm -rf tmp
}
