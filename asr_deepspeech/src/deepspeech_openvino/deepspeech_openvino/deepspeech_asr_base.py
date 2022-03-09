#!/usr/bin/env python3
"""
 Copyright (C) 2019 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import sys
import os
import numpy as np
import logging as log
from time import time
from openvino.inference_engine import IENetwork, IECore
import codecs
from deepspeech_openvino.speech_features import audio_spectrogram, mfcc
from deepspeech_openvino.ctc_beamsearch_decoder import ctc_beam_search_decoder
from abc import abstractmethod

n_input = 26
n_context = 9
n_steps = 16
numcep = n_input
numcontext = n_context
beamwidth = 10


def preprocess_sound(audio_rev, fs):
    """
    converts audio to features
    """
    audio = np.frombuffer(audio_rev, dtype=np.dtype("<h"))
    # normalize to -1 to 1, int 16 to float32
    audio = audio / np.float32(32768)
    audio = audio.reshape(-1, 1)
    spectrogram = audio_spectrogram(
        audio, (16000 * 32 / 1000), (16000 * 20 / 1000), True
    )
    features = mfcc(spectrogram.reshape(1, spectrogram.shape[0], -1), fs, 26)
    empty_context = np.zeros((numcontext, numcep), dtype=features.dtype)
    features = np.concatenate((empty_context, features, empty_context))
    num_strides = len(features) - (n_context * 2)
    # Create a view into the array with overlapping strides of size
    # numcontext (past) + 1 (present) + numcontext (future)
    window_size = 2 * n_context + 1
    features = np.lib.stride_tricks.as_strided(
        features,
        (num_strides, window_size, n_input),
        (features.strides[0], features.strides[0], features.strides[1]),
        writeable=False,
    )
    return features


class DeepSpeechASR(object):
    def __init__(self, model, device, sample_rate, alphabet_cfg="", SPEECH_LIB_PATH=""):
        # TODO asserts on model= have .xml xtension, sample rate should be a number,
        # alphabet_cfg a file name, protect it additionally, speechlib path apath
        # assert device in supported openvino devices
        self.output_text = ""
        self.cpu_extension = SPEECH_LIB_PATH
        self.sample_rate = ""
        self.model_bin = model.replace(".xml", ".bin")
        self.model_xml = model
        self.device = device
        self.alphabet_cfg = alphabet_cfg
        self.sample_rate = 16000
        self.ie = IECore()
        self.exec_net = None
        # TODO: Enable cpu extensions
        # if self.cpu_extension and 'CPU' in self.device:
        # if os.path.exists(self.cpu_extension) and 'CPU' in self.device:
        #    self.ie.add_extension(self.cpu_extension, "CPU")
        # Read IR
        log.debug(
            "DeepSpeechASR: Loading network files:\n\t{}\n\t{}".format(
                self.model_xml, self.model_bin
            )
        )
        self.net = self.ie.read_network(
            model=self.model_xml, weights=self.model_bin)
        return self._load_model_to_device()

    @abstractmethod
    def _load_model_to_device(self):
        pass

    @abstractmethod
    def _transcribe(self, features):
        pass

    def close(self):
        log.info("DeepSpeechASR: close()")
        if self.exec_net:
            del self.exec_net
        if self.ie:
            del self.ie

    def push_data(self, buffer):
        features = preprocess_sound(buffer, self.sample_rate)
        self.output_text = self._transcribe(features)

    def get_result(self, final, finish_processing):
        # TODO: do something with final
        result = self.output_text
        if finish_processing:
            self.exec_net = ""
            self._load_model_to_device()
        return result


class Alphabet(object):
    def __init__(self, alphabet_cfg):
        self._label_to_str = []
        self._str_to_label = {}
        self._size = 0
        # since file is opened using "with", no need to close explicitly
        with codecs.open(alphabet_cfg, "r", "utf-8") as fin:
            try:
                for line in fin:
                    if line[0:2] == "\\#":
                        line = "#\n"
                    elif line[0] == "#":
                        continue
                    self._label_to_str += line[:-1]  # remove the line ending
                    self._str_to_label[line[:-1]] = self._size
                    self._size += 1
            except Exception as msg:
                if fin.closed == False:
                    fin.close()
                log.error("Received Exception: {}".format(msg))

    def string_from_label(self, label):
        return self._label_to_str[label]

    def label_from_string(self, string):
        return self._str_to_label[string]

    def size(self):
        return self._size


def main():
    # TODO: Write sample app here
    # asr = DeepSpeechASR()
    pass


if __name__ == "__main__":
    main()
