# audio ingestion service

This component is helpful during development and debugging. It supports reading wave files and publish them over 0MQ using `zmq_integration_component` of converational-ai-chatbot. It can be used to run the chatbot pipline remotely when microphone is not available.

## Usage

### Using pre-recorded speech audio

It is possible to record the speech or queries using microphone on a device and use the pre-recorded clips as input to conversational ai chatbot. The pre-recorded wave files should have sample rate 16K, sample_width=2 and channel=1. It is possible to use the following command to convert wav files to this format.

```
sox input.wav -c 1 -r 16000 output.wav

```
 
The speech recognition models used in this software are trained for US accent english, so sometime it is diffcult for non native english speakers to get the accent right. Hence there is another approach that can be used while debugging/development . We can record the audio using online TTS services like [text to speech](https://texttospeech.onl/), [azure speech](https://azure.microsoft.com/en-in/services/cognitive-services/text-to-speech/#features), [aws polly](https://aws.amazon.com/polly/), [google tts](https://cloud.google.com/text-to-speech/), [free tts](https://freetts.com/) etc and use them as pre-recorded audio queries.
 

DISCLAIMER: Online TTS Services may not be free for commercial use. One should consult the policy document for more details. We don't endorse any of these services. They are mentioned only for easy reference. 


Suppose we have pre-recorded file namely  audio0.wav, audio1.wav, audio2.wav. We can keep them in a folder and map the folder to the audio_ingestion container. Then we need to set the following env variables.

- `WAVE_PATH` : It has the path of the folder with pre-recoded audio files
- `WAVE_FILES` : A comma separated list of wave file names. (don't give space after comma)

Example of audio_ingestion service using pre-recoded files. Assuming that pre-recorded audio files are in `compose/audios` folder.
```yml

services:
  wave_ingestion:
    image: "audio-ingester:1.0"
    environment:
      - OUTPUT_ADDR=ipc:///feeds/0
      - WAVE_PATH=/audios
      - WAVE_FILES=audio0.wav,audio1.wav,audio2.wav,audio3.wav
      - OUTPUT_TOPIC=audio
      - INPUT_ADDR=ipc:///feeds/11
      - INPUT_TOPIC=userloggedin
      - AUTHZ_SERVER_ADDR=ipc:///feeds/9
      - LOG_LEVEL=info
    volumes:
      - ./audios:/audios
      - zmq_ipc_vol:/feeds
    command: ["python3", "/app/src/main.py"]
    depends_on:


```

 
The `pcm16le` data published by this component can be obtained from zmq in the following way. A sample subscriber is also included in the repo.

```python
import numpy
import zmq
import json

def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    topic, array = socket.recv_multipart(flags=flags)
    print (topic.decode())
    #print (json.loads(info.decode()))
    array = np.frombuffer(array)
    return array


def main():
    try:
        TOPIC = os.environ["TOPIC"]
    except KeyError:
        TOPIC = "audio"
    try:
        PORT = os.environ["PORT"]
    except KeyError:
        PORT = 6001

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % PORT)
    
    topic = bytes(TOPIC, encoding='utf-8')
    
    socket.setsockopt(zmq.SUBSCRIBE, topic)

    f = wave.open("recieve.wav", "wb")
    f.setframerate(16000) # 16K framerate
    f.setnchannels(1) # mono 
    f.setsampwidth(2) # pcm16le

    while True:
        # receive frames here
        f.writeframes(recv_array(socket))


if __name__ == "__main__":
    main()

```
