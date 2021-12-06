# Release Notes

- [Release Notes](#release-notes)
	- [Limitations](#limitations)

***Conversational AI Chat Bot V1.5***

This software release has the following software components delivered as `dockerfiles` and python packages. The pre-build images or binaries are not hosted anywhere, so the software needs to be build on the target machine. Instructions to build the software from the `dockerfiles`  are included in _README.md_.  All component folders have _README.md_ file with instructions to build and use them. The `dockerfiles` will pull the required AI Models from OPENVINO&trade; model zoo while building, there is not need to install or download the models separately.  The scripts to generate keys and security features are also provided.

This release is intended to demonstrate the capability of Intel hardware using components optimized for Intel hardware, for AI application use case. This release is intended to be a reference software which has limitations.  This demo code uses [openbankproject](https://openbankproject.com/) client api to emulate the bank. Only a few api's are implemented for demo purposes. The demo sandbox server used in this software may not emulate an actual banking setup. This software runs the AI inference wholly on the [Edge Device](https://en.wikipedia.org/wiki/Edge_computing). Only the banking server is supposed to run on the cloud.

This release does not contain any UI component. The usage and login/logout are cli(command line interface based). `Authz` Component does session handling and login/logout for this software. While integrating this software with a software stack and UI, the SI must replace or extend this component. 

## Limitations

- Building this software from source needs a persistent network connection. It is advised to use tmux or screen when doing docker build.
- ASR Service may not infer text from speech correctly because they are trained on publicly available data.
- TTS may have quality issues for small sentences.
- TTS may have quality issues with acronyms since it is trained with publicly available data.
- Rasa 1.x generates at times different model with the same input training data.
- Open bank server sandbox used by this software may not simulate an actual bank.
- Only one user supported at a time
- Recording of audio through the ReSpeaker&trade; starts within few milliseconds after the utterance of wake-up word.
- Wake word detection may not be accurate due to limitation of ReSpeaker&trade; python sdk. which uses pocketsphinx.
