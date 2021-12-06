# ASR Service (huggingface wav2vec2-base-960h)

This service is concerned with converting speech input to text output. It can receive pcm audio data (sample_width=2, bitrate=16K) from 0MQ over a specified address and topic, and convert it to text and publish it to 0MQ on a specified topic and specified )MQ socket address. This component uses `zmq_integration_lib` to recive input and publish output to 0MQ. It uses Facebook's Wav2Vec2 model base model pretrained and fine-tuned on 960 hours of Librispeech on 16kHz sampled speech audio [https://huggingface.co/facebook/wav2vec2-base-960h].

## Pre-requisites
- 0MQ
- transformers
- python3

## Data Formats

| Input Format  | Output Format         |
| ------------- | --------------------- |
| bytes (pcm data, mono, 16K sample rate, sample_witdh =2) | bytes (unicode string) |

*The input audio buffer should be sent with an event 'pcm'. [details here](#input-data-format)*
NOTE: A string can be obtained from byte encoded out buffer using `.decode()` method. `data_string = data.decode()`


## Model

When using the dockerfile, the model is automatically downloaded.

## Build

Using the bundled dockerfile.
```
docker build -f dockerfiles/huggingface_asr.dockerfile -t huggingface_asr:1.0 .
```

or
```
make docker
```

## Run

```
docker run --rm  -e INPUT_TOPIC='audio' -e  INPUT_PORT='6001' -e OUTPUT_TOPIC='text' -e OUTPUT_PORT='6002' -it huggingface_asr .
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

Huggingface ASR container supports pcm data (16K mono channel) sent as a single buffer. The audio ingestion component, using zmq_integration_lib, should send data as:


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

