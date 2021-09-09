#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from tts_openvino.synthesizer import Synthesizer


class tacotron_tts:
    def __init__(self):
        duration_model = "/model/text-to-speech-en-0001-duration-prediction.xml"
        regression_model = "/model/text-to-speech-en-0001-regression.xml"
        generation_model = "/model/text-to-speech-en-0001-generation.xml"
        self.synthesizer = Synthesizer()
        self.synthesizer.load(
            duration_model, regression_model, generation_model)

    def get_speech_fortext(self, text):
        return self.synthesizer.synthesize(text)


def main():
    T = tacotron_tts()
    text_for_tts = "Listen to this voice, this is not a real person speaking. I am a text to speech software powered by Intel"

    speech = T.get_speech_fortext(text_for_tts)
    filename = "file.wav"
    open(filename, "wb").write(speech)


if __name__ == "__main__":
    main()
