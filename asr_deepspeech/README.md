# ASR Service (Deepspeech)

This service is concerned with converting speech input to text output. It can receive pcm audio data (sample_width=2, bitrate=16K) from 0MQ over a specified address and topic, and convert it to text and publish it to 0MQ on a specified topic and specified )MQ socket address. This component uses `zmq_integration_lib` to recive input and publish output to 0MQ. It uses OpenVINO&trade; and deepspeech. Deepspeech is based on the [sample code on OpenVINO&trade; model zoo](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/text_to_speech_demo/python).

## Pre-requisites
- 0MQ
- OpenVINO&trade; 2021.3
- python3

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (pcm data, mono, 16K sample rate, sample_witdh =2) | bytes (unicode string) |

*The input audio buffer should be sent with an event 'pcm'. [details here](#input-data-format)*
NOTE: A string can be obtained from byte encoded out buffer using `.decode()` method. `data_string = data.decode()`


## Model

When using the dockerfile, the model is automatically downloaded.

### DeepSpeech Version 0.8.2

The model can be downloaded using the `open mode zoo`'s model downloader.
A uitlity script to download the model is kept at `scripts/download_model.sh`. It can be used as:

```bash
source /opt/intel/openvino/bin/setupvars.sh
cd scripts
./download_model.sh
```

To use deepspeech version 0.8.2, the deepspeech config file must have

```
-inference:model_xml "/model/public/mozilla-deepspeech-0.8.2/FP32/mozilla-deepspeech-0.8.2.xml"
-inference:model_bin "/model/public/mozilla-deepspeech-0.8.2/FP32|speech release 0.5.0](https://github.com/mozilla/DeepSpeech/rele
/mozilla-deepspeech-0.8.2.xml"
-inference:lm "/model/public/mozilla-deepspeech-0.8.2/deepspeech-|vinotoolkit.org/latest/_docs_MO_DG_prepare_model_convert_model_t
0.8.2-models.kenlm"
-deepspeech:version: 8

```

A sample config file for using deepspeech version 8 is `src/model/deepspeech8.cfg`.
This would be the default version used by deepspeech.

## Build

Using the bundled dockerfile.
```
docker build -f asr_deepspeech/Dockerfile -t deepspeech_asr:1.0 .
```

or
```
make docker
```

## Run

```
docker run --rm  -e INPUT_TOPIC='audio' -e  INPUT_PORT='6001' -e OUTPUT_TOPIC='text' -e OUTPUT_PORT='6002' -it deepspeech_asr .
```

or

```
make run
```

Following environment variables are required by this service.

| ENV Variable  | Description       |
| ------------- | --------------------- |
| INPUT_ADDR | It is the address of 0MQ socket. |
| INPUT_TOPIC | It is the topic on which 0MQ input is received. |
| OUTPUT_ADDR |It is 0MQ socket address on which asr text is published. |
| OUTPUT_TOPIC | It is the topic on which this service will publish text output data. |
| AUTHZ_SERVER_ADDR | It is the address of 0MQ socket of `authz` rpc server. |
| LOG_LEVEL | It can have values info, debug, warning, error. |

## Input Data Format

Deepspeech container supports pcm data (16K mono channel) sent as a single buffer. The audio ingestion component, using zmq_integration_lib, should send data as:


```
import zmq_integration_lib as IL
import wave

Outport = IL.OutputPort("tcp://*:6001", TOPIC)

def publish_pcm(Outport, file):
    import wave
    with wave.open(file) as f:
       pcm_data = f.readframes(-1)
       return Outport.push(pcm_data, "pcm")

publish_pcm(Outport, "somefile.wav")
```

## Components of `asr service (deepspeech)`

- `src/speech_library`
   It has a speech manager and a speech proxy component. It is similar to openvino speech library's(kaldi) python package. Application can use speech_manager to convert speech to text. It expects a config file with model parameters. A sample config file is at `src/model/deepspeech8.cfg`. An example to use it is found at `src/speech_library/examples`
- `src/asr`
   It is an abstraction which supports parsing of config file and it depends on `deepspeech_openvino` to convert speech to text.
- `src/deepspeech_openvino`
   It is a python package which can infer text output from speech using deepspeech models. It supports deepspeech v5 and v8. v8 is recommended. It is based on [sample code on OpenVINO&trade; model zoo](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/text_to_speech_demo/python). An example to use this package is found at `src/deepspeech_openvino/examples`.


## Limitations

- supports audio input which is mono channel sampled at 16K and represented with 2 bytes per sample.
- supports US english accent.
- text output for non US english accents may be bad.
