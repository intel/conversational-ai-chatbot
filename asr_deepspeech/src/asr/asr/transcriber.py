"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import logging as log
from asr.configparser import parse_config, parser
from deepspeech_openvino.deepspeech_asr_v5 import DeepSpeechv5
from deepspeech_openvino.deepspeech_asr_v7 import DeepSpeechv7
from deepspeech_openvino.deepspeech_asr_v8 import DeepSpeechv8


class SpeechTranscriber(object):
    def __init__(self, SPEECH_LIB_PATH=""):
        self.speech_lib_path = SPEECH_LIB_PATH

    def initialize(self, asr_config):
        (
            model_xml,
            model_bin,
            device,
            alphabet_cfg,
            sample_rate,
            version,
            lm,
        ) = parse_config(asr_config)
        try:
            if int(version) == 7:
                self.speech_transcriber = DeepSpeechv7(
                    model=model_xml,
                    device="CPU",
                    alphabet_cfg=alphabet_cfg,
                    sample_rate=sample_rate,
                    SPEECH_LIB_PATH=self.speech_lib_path,
                )
            elif int(version) == 5:
                self.speech_transcriber = DeepSpeechv5(
                    model=model_xml,
                    device="CPU",
                    alphabet_cfg=alphabet_cfg,
                    sample_rate=sample_rate,
                    SPEECH_LIB_PATH=self.speech_lib_path,
                )
            elif int(version) == 8:
                # lm = parser("lm", asr_config)
                self.speech_transcriber = DeepSpeechv8(
                    model=model_xml,
                    device="CPU",
                    alphabet_cfg=alphabet_cfg,
                    sample_rate=sample_rate,
                    lang_model=lm,
                    SPEECH_LIB_PATH=self.speech_lib_path,
                )
            else:
                return False
            return True
        except Exception as msg:
            log.error("SpeechTranscriber: %s", msg)
            return False

    def close(self):
        self.speech_transcriber.close()

    def push_data(self, buffer):
        return self.speech_transcriber.push_data(buffer)

    def get_result(self, final, finish_processing):
        return self.speech_transcriber.get_result(final, finish_processing)
