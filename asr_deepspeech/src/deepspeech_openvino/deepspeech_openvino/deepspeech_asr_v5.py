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

import logging as log
from openvino.inference_engine import IENetwork, IECore
from deepspeech_openvino.deepspeech_asr_base import DeepSpeechASR
import codecs
from deepspeech_openvino.ctc_beamsearch_decoder import ctc_beam_search_decoder
import numpy as np

beamwidth = 10
n_steps = 16


class DeepSpeechv5(DeepSpeechASR):
    def _load_model_to_device(self):
        # TODO: Add some asserts here for net etc which should be present
        # before this is called
        if len(self.net.inputs.keys()) != 3:
            raise Exception("The Sample supports only three input topologies")
        if len(self.net.outputs) != 3:
            raise Exception("The Sample supports only three output topologies")
        # assert len(self.net.outputs) == 3, "Sample supports only three output topologies"

        log.debug("DeepSpeechv5: Preparing input blobs")
        input_iter = iter(self.net.inputs)
        input_blob1 = next(input_iter)
        input_blob2 = next(input_iter)
        input_blob3 = next(input_iter)

        log.debug("DeepSpeechv5: Preparing output blobs")
        output_iter = iter(self.net.outputs)
        output_blob1 = next(output_iter)
        output_blob2 = next(output_iter)
        output_blob3 = next(output_iter)
        # Loading model to the plugin
        log.debug("DeepSpeechv5: Loading model to the plugin")
        try:
            if self.exec_net:
                del self.exec_net
        except Exception as msg:
            log.debug(
                "DeepSpeechv5: Couldn't cleaunup previous exec_net: %s", msg)
        self.exec_net = self.ie.load_network(
            network=self.net, device_name=self.device)
        self.state_h = np.zeros((1, 2048))
        self.state_c = np.zeros((1, 2048))
        # Loading model to the plugin
        alphabet = Alphabet(self.alphabet_cfg)
        self.logits = np.empty([0, 1, alphabet.size()])
        log.info("DeepSpeechv5: Loaded model to device")

    def _transcribe(self, features):
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
                    "previous_state_c/read/placeholder_port_0": self.state_c,
                    "previous_state_h/read/placeholder_port_0": self.state_h,
                    "input_node": [chunk],
                }
            )
            # Processing output blob
            # log.info("Processing output blob")
            self.logits = np.concatenate((self.logits, res["Softmax"]))
            self.state_h = res["lstm_fused_cell/BlockLSTM/TensorIterator.1"]
            self.state_c = res["lstm_fused_cell/BlockLSTM/TensorIterator.2"]
        alphabet1 = Alphabet(self.alphabet_cfg)
        self.text = "{} ".format(
            ctc_beam_search_decoder(
                self.logits,
                alphabet1._label_to_str,
                alphabet1.string_from_label(-1),
                beamwidth,
            )
        )
        return self.text


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
