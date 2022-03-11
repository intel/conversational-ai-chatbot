# ASR Service (KALDI)

`ASR Service` is based on [speech_library](https://docs.openvinotoolkit.org/latest/openvino_inference_engine_samples_speech_libs_and_demos_Speech_library.html) of OpenVINO&trade; It uses KALDI&trade; model. It can receive pcm audio data (sample_width=2, bitrate=16K) from 0MQ over a specified address and topic, and convert it to text and publish it to 0MQ on a specified topic and specified 0MQ socket address. This component uses `zmq_integration_lib` to recive input and publish output to 0MQ.

## Pre-requisites
- 0MQ
- OpenVINO&trade; 2021.3
- python3
- docker


## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (pcm data, 16K sample rate, sample_width =2) | bytes (unicode string) |

*The input audio buffer should be sent with an event 'pcm'. [details here](#input-data-format)*

NOTE: A string can be obtained from byte encoded out buffer using `.decode()` method. `data_string = data.decode()`

## Build

```
cd <repo-root>
make kaldi_asr
```


## Run

### Download models

The models are hosted by OpenVINO&trade;. We can use `model downloader` of OpenVINO&trade model zoo; to download the model. The yml file with location of the model is kept at `<repo-root>/asr_kaldi/src/model/lspeech_s5_ext.yml`.

A utility script to download the model has been kept at `<repo-root>/asr_kaldi/scripts/download_model.sh`. It can be used as:

```bash
# make sure python3-venv is installed
<repo-root>/asr_kaldi/scripts/download_model.sh -c <repo-root>/asr_kaldi/src/model/lspeech_s5_ext.yml -d some_model_path
```

A sample compose.yml to run the application.

```yml
  asr_speech:
    image: "kaldi_asr:1.0"
    environment:
      - OUTPUT_ADDR=ipc:///feeds/1
      - OUTPUT_TOPIC=text
      - INPUT_TOPIC=audio
      - INPUT_ADDR=ipc:///feeds/0
      - AUTHZ_SERVER_ADDR=ipc:///feeds/9
      - LOG_LEVEL=debug
    volumes:
      - zmq_ipc_vol:/feeds
    depends_on:
      - nlp_app
```

Following environment variables are required by this service.

| ENV Variable  | Description       |
| ------------- | --------------------- |
| INPUT_ADDR | It is the address of 0MQ socket. |
| INPUT_TOPIC | It is the topic on which 0MQ input is recieved. |
| OUTPUT_ADDR |It is 0MQ socket address on which asr text output is published. |
| OUTPUT_TOPIC | It is the topic on which asr service will publish text output. |
| AUTHZ_SERVER_ADDR | It is the address of 0MQ socket of `authz` rpc server. |
| LOG_LEVEL | It can have values info, debug, warning, error. |

## Input Data Format

kaldi asr container supports pcm data (16K mono channel) sent as a single buffer. The audio ingestion component, using zmq_integration_lib, should send data as:


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

## Standalone utilty

A stand alone utility for speech to text with KALDI model is kept in `<repo-root>/asr_kaldi/scripts/asr.h`. It can be used to convert any wave audio file with 16K bitrate and 2 byte sample width to text.

```
# suppose input file is input.wav in the current directory

docker run --rm -it -v $(pwd):/data kaldi_asr:1.0 bash -c "/app/asr.sh -c /model/speech_lib.cfg -i /data/input.wav"

```

## Limitations

- It supports only english language
- It supports american accent.
- It is based on lspeech data so output may be limited.
- supports audio input which is mono channel sampled at 16K and represented with 2 bytes per sample.
