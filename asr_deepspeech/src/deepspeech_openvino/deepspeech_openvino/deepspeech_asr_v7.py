#!/usr/bin/env python
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
import numpy as np
import logging as log
import time
from openvino.inference_engine import IENetwork, IECore
from deepspeech_openvino.ctc_beamsearch_decoder import ctc_beam_search_decoder
from deepspeech_openvino.deepspeech_asr_base import DeepSpeechASR
import codecs

beamwidth = 10
n_steps = 16


class DeepSpeechv7(DeepSpeechASR):
    def _load_model_to_device(self):
        assert (
            len(self.net.inputs.keys()) == 3
        ), "Sample supports only three input topologies"
        self.alphabet = " abcdefghijklmnopqrstuvwxyz'-"
        assert (
            len(self.net.outputs) == 3
        ), "Sample supports only three output topologies"
        log.debug("DeepSpeechv7: Loading model to the plugin")
        try:
            if self.exec_net:
                del self.exec_net
        except Exception:
            log.debug(
                "DeepSpeechv5: Couldn't cleaunup previous exec_net: {}".format(e))
        self.exec_net = self.ie.load_network(
            network=self.net, device_name=self.device)
        self.state_h = np.zeros((1, 2048))
        self.state_c = np.zeros((1, 2048))
        self.logits = np.empty([0, 1, len(self.alphabet)])
        log.debug("DeepSpeechv7: Loaded model to device")

    def close(self):
        log.info("DeepSpeechv7: close()")
        if self.exec_net:
            del self.exec_net
        if self.ie:
            del self.ie

    def _transcribe(self, features):
        probs = []
        for i in range(0, len(features), n_steps):
            chunk = features[i: i + n_steps]
            if len(chunk) < n_steps:
                chunk = np.pad(
                    chunk,
                    ((0, n_steps - len(chunk)), (0, 0), (0, 0)),
                    mode="constant",
                    constant_values=0,
                )
            res = self.exec_net.infer(
                inputs={
                    "previous_state_c": self.state_c,
                    "previous_state_h": self.state_h,
                    "input_node": [chunk],
                }
            )
            # Processing output blob
            self.logits = np.concatenate((self.logits, res["logits"]))
            self.state_h = res[
                "cudnn_lstm/rnn/multi_rnn_cell/cell_0/cudnn_compatible_lstm_cell/BlockLSTM/TensorIterator.1"
            ]
            self.state_c = res[
                "cudnn_lstm/rnn/multi_rnn_cell/cell_0/cudnn_compatible_lstm_cell/BlockLSTM/TensorIterator.2"
            ]
            probs.append(res["logits"].squeeze(1))
        probs = np.concatenate(probs)
        # self.text = "{} ".format(ctc_beam_search_decoder(self.logits, self.alphabet, self.alphabet[-1], beamwidth))
        # self.output_text = self.text
        alphabet1 = Alphabet(self.alphabet_cfg)
        self.text = "{} ".format(
            ctc_beam_search_decoder(
                probs,
                alphabet1._label_to_str,
                alphabet1.string_from_label(-1),
                beamwidth,
            )
        )
        self.output_text = self.text
        return self.output_text


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
