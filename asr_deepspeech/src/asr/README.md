# ASR Transcriber

It is a wrapper to use deepspeech openvino ASR. It can read the speech lib config and instantiate 
an deepspeech asr component. It can instantiate deepspeech v5, v7 and v8 based on the config file.
It is used by `speech_library` component. It requires `deepspeech_openvino` component to work.

## Install

```
# deepspeech_openvino and openvino must be instaled
python setup.py install
```

## Config 

This is the example config file needed by this component.

```
-fe:rt:alphabet_config "/model/alphabet_b.txt"
-fe:rt:inputDataType INT16_16KHz
-fe:rt:maxChunkSize 16000
-inference:device CPU
-inference:model_xml "/model/public/mozilla-deepspeech-0.8.2/FP32/mozilla-deepspeech-0.8.2.xml"
-inference:model_bin "/model/public/mozilla-deepspeech-0.8.2/FP32/mozilla-deepspeech-0.8.2.xml"
-inference:lm "/model/public/mozilla-deepspeech-0.8.2/deepspeech-0.8.2-models.kenlm"
-deepspeech:version: 8 

```

