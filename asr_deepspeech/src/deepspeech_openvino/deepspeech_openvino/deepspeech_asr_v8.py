#!/usr/bin/env python3
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
# This file is based on https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/python_demos/speech_recognition_demo
#

import wave
import timeit
import argparse
import yaml
import numpy as np
from tqdm import tqdm
from deepspeech_openvino.utils.context_timer import Timer
from deepspeech_openvino.utils.deep_speech_pipeline import DeepSpeechPipeline, PROFILES
from deepspeech_openvino.deepspeech_asr_base import DeepSpeechASR


def preprocess_sound(audio_rev, stt):
    sampling_rate = 16000
    audio = np.frombuffer(audio_rev, dtype=np.dtype("<h"))
    # normalize to -1 to 1, int 16 to float32
    audio = audio / np.float32(32768)
    audio = audio.reshape(-1, 1)
    audio_features = stt.extract_mfcc(audio, sampling_rate=sampling_rate)
    return audio_features


def get_profile(profile_name):
    if profile_name in PROFILES:
        return PROFILES[profile_name]
    # since file is opened using "with", no need to close explicitly
    with open(profile_name, "rt") as f:
        try:
            profile = yaml.safe_load(f)
        except:
            if f.closed == False:
                f.close()
        return profile


beam_width = 500
max_candidates = 1


class DeepSpeechv8(DeepSpeechASR):
    def __init__(
        self,
        model,
        device,
        sample_rate,
        alphabet_cfg="",
        lang_model="",
        SPEECH_LIB_PATH="",
    ):
        # TODO asserts on model= have .xml xtension, sample rate should be a number,
        self.lm = lang_model
        super().__init__(
            model=model,
            device=device,
            sample_rate=sample_rate,
            alphabet_cfg=alphabet_cfg,
            SPEECH_LIB_PATH=SPEECH_LIB_PATH,
        )

    def _load_model_to_device(self):
        self.profile = get_profile("mds08x_en")
        self.stt = DeepSpeechPipeline(
            model=self.model_xml,
            lm=self.lm,
            beam_width=beam_width,
            max_candidates=max_candidates,
            profile=self.profile,
            device=self.device,
        )

    def push_data(self, buffer):
        audio_features = preprocess_sound(buffer, self.stt)
        # character_probs = self.stt.extract_per_frame_probs(audio_features, wrap_iterator=tqdm)
        character_probs = self.stt.extract_per_frame_probs(audio_features)
        transcription = self.stt.decode_probs(character_probs)
        # print(transcription)
        for candidate in transcription:
            self.text = "{} ".format(candidate["text"])
            # print(self.text)
        self.output_text = self.text

    def _transcribe(self, features):
        pass

    def get_result(self, final, finish_processing):
        # TODO: do something with final
        result = self.output_text
        if finish_processing:
            self.exec_net = ""
            import time

            # self.stt.activate_model(self.stt.default_device)
        return result
