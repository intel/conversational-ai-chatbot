# TTS (Text to Speech) Service

TTS (Text to Speech) service runs as an independant docker container. It can subscribe to 0MQ and convert the streaming text input to wav audio. It can publish the wav audio output onto 0MQ over a predefined topic. Additionally it has a feature to play the wav audio to the sound device(s).

It uses `tts_openvino` which is based on modified ForwardTacotron and melgan vocoder accelerated via OpenVINO&trade;. It is based on the TTS sample hosted on [openvino model zoo](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/text_to_speech_demo/python).

## Pre-requisites

- OpenVINO&trade; 2021.3 docker image
- docker 19.03 or greater
- audio hardware (speaker/headphones)

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (unicode string) | bytes (wave file) |

NOTE: A string can be obtained from byte encoded input/out buffer using `.decode()` method. `data_string = data.decode()`


## Run

An example docker-compose.yml service.
```
  tts:
    image: "tts:1.0"
    devices:
      - /dev/snd:/dev/snd
    environment:
      - INPUT_ADDR=ipc:///feeds/2
      - INPUT_TOPIC=nlp
      - OUTPUT_ADDR=ipc:///feeds/3
      - OUTPUT_TOPIC=tts
      - AUTHZ_SERVER_ADDR=ipc:///feeds/9
      - LOG_LEVEL=debug
      - PLAY_AUDIO=1
    command: ["./run.sh"]
    volumes:
      - zmq_ipc_vol:/feeds

```


Following environment variables are required by this service.

| ENV Variable  | Description       |
| ------------- | --------------------- |
| INPUT_ADDR | It is the address of 0MQ socket. |
| INPUT_TOPIC | It is the topic on which 0MQ input is recieved. |
| OUTPUT_ADDR |It is 0MQ socket address on which wave data is published. |
| OUTPUT_TOPIC | It is the topic on which tts service will publish pcm wave data. |
| AUTHZ_SERVER_ADDR | It is the address of 0MQ socket of `authz` rpc server. |
| LOG_LEVEL | It can have values info, debug, warning, error. |
| PLAY_AUDIO | (optional) If the variable is set, tts service will play the audio. |


## Limitations

- It is based on pretrained models which are downloaded from openVINO&trade; model zoo.
- It supports english language only.
