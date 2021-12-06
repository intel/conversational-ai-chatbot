# Audio Ingestion Service

This service can record audio from microphone and publish it to 0MQ on a specified port and topic. It uses [respeaker sdk](https://github.com/respeaker/respeaker_python_library.git). It needs respeaker micarrays/microphones to work with.

This service subscribes to the `authz` component for session-id. It gets session-id when the user does a login at `authz` component. After getting the session id, this service can start recording and publishing data to 0MQ output. 

NOTE: Using a non respeaker microphone with this audio ingestion is not supported as of now.

## Requirements

- docker >= 19.03.5
- python3
## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (unicode string) | bytes (pcm audio) 16K samplerate, sample_width=2, mono channel |

## Usage

The compose.yml for the service loks like


```yml
services:
  audio_ingestion:
    image: "audio-ingester2:${TAG}"
    devices:
      - /dev/snd:/dev/snd
    environment:
      - INPUT_ADDR=ipc:///feeds/11
      - INPUT_TOPIC=userloggedin
      - OUTPUT_ADDR=ipc:///feeds/0
      - OUTPUT_TOPIC=audio
      - AUTHZ_SERVER_ADDR=ipc:///feeds/9
      - WAKE_UP_WORD=chatbot
      - LOG_LEVEL=debug
    command: ["bash", "/app/run.sh"]
    volumes:
      - zmq_ipc_vol:/feeds
    depends_on:
     - tts
```


Following environment variables are required by this service.

| ENV Variable  | Description       |
| ------------- | --------------------- |
| INPUT_ADDR | It is the address of 0MQ socket. |
| INPUT_TOPIC | It is the topic on which 0MQ input is recieved. |
| OUTPUT_ADDR |It is 0MQ socket address on which pcm is published. |
| OUTPUT_TOPIC | It is the topic on which audio ingestion will publish pcm wave data. |
| AUTHZ_SERVER_ADDR | It is the address of 0MQ socket of `authz` rpc server. |
| LOG_LEVEL | It can have values info, debug, warning, error. |
| WAKE_UP_WORD | It can be: *respeaker*, *intel*, *chatbot*, *kiosk* |

## Limitations

- Supports only predefined wake words as of now. However they can be extended.
