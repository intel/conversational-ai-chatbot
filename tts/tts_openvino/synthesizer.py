#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
"""

import io
import audioop
import numpy as np
import scipy.io.wavfile

from tts_openvino.models.forward_tacotron_ie import ForwardTacotronIE
from tts_openvino.models.mel2wave_ie import MelGANIE
from openvino.inference_engine import IECore


def _resample_nparray(arr, old_sample_rate, new_sample_rate):
    # expects array to be of dtype=np.short, mono channel audio
    channel = 1
    sample_width=2
    pcm = arr.tobytes()
    resampled_data, _ = audioop.ratecv(pcm, sample_width, channel , old_sample_rate, new_sample_rate, None)
    return np.frombuffer(resampled_data, dtype=np.short)


def save_wav(x, path):
    data_sample_rate = 22050
    new_sample_rate = 16000
    # resample data to 16K
    arr = _resample_nparray(x, data_sample_rate, new_sample_rate)
    scipy.io.wavfile.write(path, new_sample_rate, arr)


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
