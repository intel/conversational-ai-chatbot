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
        log.debug("Initializing the Synthesizer from TTS Openvino")
        self.synthesizer = Synthesizer()
        log.debug("Loading the model")
        self.synthesizer.load(
            config.duration_model, config.regression_model, config.generation_model
        )
        log.debug("TTS Model Loaded")

    def get_speech_fortext(self, text):
        return self.synthesizer.synthesize(text)


def main():
    log.info("Starting TTS Service")
    T = tacotron_tts()

    ip = config.get_inputport()
    log.info("Created 0MQ Input Data Receiver")
    out = config.get_outputport()
    log.info("Created Output Data Publisher")

    log.debug("Waiting to Receive Input Data")
    for text_b, event in ip.data_and_event_generator():
        try:
            log.debug("Decode Input bytes to utf-8")
            text = text_b.decode()
            speech = T.get_speech_fortext(text)
            if config.PLAY_AUDIO:
                log.debug("Playing Audio Reply")
                config.play_audio(speech)
            log.debug("Publishing Data to 0MQ")
            out.push(speech)
        except Exception as msg:
            log.error("Got an exception: %s", msg)


if __name__ == "__main__":
    main()
