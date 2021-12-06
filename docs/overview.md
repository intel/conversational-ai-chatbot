# Overview

- [Overview](#overview)
  - [Appendix](#appendix)

The **Conversational AI Chat Bot** has the following components:

- `ASR Service`
    ASR(Automatic Speech Recognition) converts the speech audio to text. It can be one of these ([KALDI&trade;](https://docs.openvinotoolkit.org/latest/omz_demos_text_to_speech_demo_python.html), [deepspeech&trade;](https://docs.openvinotoolkit.org/latest/omz_demos_speech_recognition_deepspeech_demo_python.html); [Quartznet](https://docs.openvinotoolkit.org/latest/omz_demos_speech_recognition_quartznet_demo_python.html), [huggingface wave2vec](https://huggingface.co/facebook/wav2vec2-base-960)

- `Audio Ingestion Service`
    It can record speech audio via microphone. Additionally it is possible to give a pre-recoded audio input via wave files. This is useful while remote development and debugging.

- `TTS Service`
    It converts the text input to speech output. It is based on openVINO tts sample which has `forward tacotron + melgan` optimised for Intel&reg; hardware.

- `ZMQ Integration Library`
    It is the library used by the services to communicate. It provides async pub/sub messaging and rpc support. It abstracts user session handling too. 

- `Authz Service`
    It provides session management and user   authentication. It hosts rpc servers which are   used by the other services for session   verification and logout.

Detailed `README`  files are kept in the folders for each component. 

## Appendix

ASR: Automatic Speech Recognition

TTS: Text to Speech

NLP: Natural Language Processing

DL: Deep Learning

OpenVINO&trade;: A Deep Learning deployment toolkit for Intel CPU/GPU/VPU/Neural devices.
