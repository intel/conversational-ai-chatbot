#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import io
import numpy as np
import scipy.io.wavfile

from tts_openvino.models.forward_tacotron_ie import ForwardTacotronIE
from tts_openvino.models.mel2wave_ie import MelGANIE
from openvino.inference_engine import IECore


def save_wav(x, path):
    sr = 22050
    scipy.io.wavfile.write(path, sr, x)


class Synthesizer:
    def load(self, duration_model, regression_model, generation_model, device="CPU"):
        self.ie = IECore()
        self.voc_melgan = MelGANIE(generation_model, self.ie, device=device)
        self.tts_model = ForwardTacotronIE(
            duration_model, regression_model, self.ie, device, verbose=False
        )

    def synthesize(self, input_text):
        mel = self.tts_model.forward(input_text)
        audio_res = self.voc_melgan.forward(mel)
        out = io.BytesIO()
        save_wav(np.array(audio_res).astype(np.short), out)
        return out.getvalue()
