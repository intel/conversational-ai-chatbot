# tts_openvino

It is a python package which can synthesize audio output from text input. It uses modified ForwardTacotron and a melgan vocoder. It uses OpenVINO™ for inference. It is based on the TTS sample hosted on [openvino model zoo](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/text_to_speech_demo/python).


## Pre-requisites
- python3
- OpenVINO&trade; 2021.3
- models

## Install

The install script will download the OpenVINO&trade; TTS sample from open model zoo and package it into an installable python package.

```
./prepare_and_install.sh

```

## Usage

### Download the models

The models are not bundled with the package. They have to be downloaded independantly. The models can be download using `model downloader` of OpenVINO&trade;.

```
$ source /opt/intel/openvino/bin/setupvars.sh
$ cd /opt/intel/openvino_2021.3.394/deployment_tools/tools/model_downloader && python3 downloader.py --print_all | grep text-to-speech > models.lst
$ cd /opt/intel/openvino_2021.3.394/deployment_tools/tools/model_downloader && python3 downloader.py --list models.lst
# The downloaded models can be found at
intel/text-to-speech-en-0001/text-to-speech-en-0001-regression/FP32

```

### Using `tts_openvino`

```python
from tts_openvino.synthesizer import Synthesizer
import wave

# Update the paths of downloaded models
duration_model = "/model/text-to-speech-en-0001-duration-prediction.xml"
regression_model = "/model/text-to-speech-en-0001-regression.xml"
generation_model = "/model/text-to-speech-en-0001-generation.xml"

# Create a TTS Synthesizer
synthesizer = Synthesizer()
synthesizer.load(duration_model, regression_model, generation_model)
wave_data = synthesizer.synthesize(text)

with open('test.wav', 'wb') as f:
	f.write(wave_data)

```

The output format is a `wave` file buffer. The bitrate of `wave` is 16K and sample width is 2.

## Limitations

- It supports English language models.
- Accuracy and quality depends on the model and the data on which it is trained.
