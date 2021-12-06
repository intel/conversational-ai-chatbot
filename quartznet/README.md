# ASR Service (QuartzNet)

This service is concerned with converting speech input to text output. It can receive pcm audio data (sample_width=2, bitrate=16K) from 0MQ over a specified address and topic, and convert it to text and publish it to 0MQ on a specified topic and specified )MQ socket address. This component uses `zmq_integration_lib` to recive input and publish output to 0MQ. It uses OpenVINO&trade; and quartznet. Quartznet is based on the [sample code on OpenVINO&trade; model zoo](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/text_to_speech_demo/python).

## Pre-requisites
- 0MQ
- OpenVINO&trade; 2021.4
- python3

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (pcm data, mono, 16K sample rate, sample_witdh =2) | bytes (unicode string) |

*The input audio buffer should be sent with an event 'pcm'. [details here](#input-data-format)*
NOTE: A string can be obtained from byte encoded out buffer using `.decode()` method. `data_string = data.decode()`


## Model

When using the dockerfile, the model is automatically downloaded.

### Download QuartzNet model

The model can be downloaded using the `open mode zoo`'s model downloader. 
A uitlity script to download the model is kept at `quartzDownloader.sh`. It can be used as:

```bash
source /opt/intel/openvino/bin/setupvars.sh
./quartzDownloader.sh
```

## Build

Using the bundled dockerfile.
```
docker build -f dockerfiles/quartznet_asr.dockerfile -t quartznet_asr:1.0 .
```

or
```
make docker
```

## Run

```
docker run --rm  -e INPUT_TOPIC='audio' -e  INPUT_PORT='6001' -e OUTPUT_TOPIC='text' -e OUTPUT_PORT='6002' -it quartznet_asr .
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

Quartznet container supports pcm data (16K mono channel) sent as a single buffer. The audio ingestion component, using zmq_integration_lib, should send data as:


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

## Limitations

- supports audio input which is mono channel sampled at 16K and represented with 2 bytes per sample.
- QuartzNet model is pre-trained on WSJ, LibriSpeech and Mozilla's Common Voice En. pre-trained QuartzNet model is fine-tuned in NGC with Wall Street Journal data.
