#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from tts_openvino.synthesizer import Synthesizer
import _config as config


log = config.get_logger()


class tacotron_tts:
    def __init__(self):
        self.synthesizer = Synthesizer()
        self.synthesizer.load(
            config.duration_model, config.regression_model, config.generation_model
        )

    def get_speech_fortext(self, text):
        return self.synthesizer.synthesize(text)


def main():
    T = tacotron_tts()

    ip = config.get_inputport()
    out = config.get_outputport()

    for text_b, event in ip.data_and_event_generator():
        try:
            text = text_b.decode()
            speech = T.get_speech_fortext(text)
            if config.PLAY_AUDIO:
                config.play_audio(speech)
            out.push(speech)
        except Exception as msg:
            log.error("Got an exception: %s", msg)


if __name__ == "__main__":
    main()
