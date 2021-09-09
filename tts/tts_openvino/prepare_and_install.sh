#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

download_sample() {

echo "Download openmodel zoo"
mkdir -p tmp/tts_openvino

#Download code for tts sample from location
cd tmp && wget https://github.com/openvinotoolkit/open_model_zoo/archive/refs/tags/2021.3.zip \
	    && unzip 2021.3.zip && cd -

cp -rf tmp/open_model_zoo-2021.3/demos/text_to_speech_demo/python tmp/tts_openvino
sed -i '190s/800/80/' tmp/tts_openvino/python/models/mel2wave_ie.py
rm -rf tmp/open_model_zoo-2021.3
}


install_tts_openvino() {

echo "Prepare module"
cp synthesizer.py tmp/tts_openvino/python

# Edit paths for imports to convert this into a package

sed -i 's/utils.numbers/tts_openvino.utils.numbers/g' tmp/tts_openvino/python/utils/text_preprocessing.py
sed -i 's/utils.text_preprocessing/tts_openvino.utils.text_preprocessing/g' tmp/tts_openvino/python/models/forward_tacotron_ie.py 
sed -i 's/utils./tts_openvino.utils./g' tmp/tts_openvino/python/models/mel2wave_ie.py 

mv tmp/tts_openvino/python tmp/tts_openvino/tts_openvino
python3 -mpip install -r tmp/tts_openvino/tts_openvino/requirements.txt
cp setup.py tmp/tts_openvino/ 
cd tmp/tts_openvino && python3 -m pip install .

}


#
echo $1
case $1 in 
  "download") 
    download_sample tmp
		;;
	"install")
	  install_tts_openvino tmp

		;;

  "clean") 
    rm -rf tmp
		;;
	
esac



