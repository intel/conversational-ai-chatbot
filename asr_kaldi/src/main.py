"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import io
import wave
from threading import Thread, RLock
from speech_library.speech_manager import SpeechManager
from multiprocessing import freeze_support
import numpy as np
import scipy.io.wavfile as sv
from zmq_integration_lib import InputPortWithEvents, OutputPort
import _config as config

log = config.get_logger()


def pusher(manager, port):
    Final = False
    data = ""
    while not Final:
        data, Final = manager.get_result()
        log.info("in thread: data [ {} ] final [ {} ]".format(data.decode(), Final))
    port.push(bytes(pretty(data), encoding="utf-8"), "FINAL")


def pretty(text):
    text_ = text.decode()
    return " ".join(text_.replace("<UNK>", " ").split()).lower()


def main():
    freeze_support()
    log.info("Kaldi ASR")

    # Set Input and Output Ports
    ipp = config.get_inputport()
    log.info("Main: Input port set")

    Outport = config.get_outputport()
    log.info("Main: Output port set")

    manager = SpeechManager()
    config_file = "/app/src/model/speech_lib.cfg"
    manager.initialize(config_file)
    log.info("Main: Speech Manager Initialized")
    try:
        for data, event in ipp.data_and_event_generator():
            if event == "pcm":
                process_pcm_data(data, manager, Outport)
                continue
    except Exception as msg:
        log.info("Received Exception %s", msg)


# This function expects the data as, bytes read from a wave file.
# bitrate,16000:mono channel and pcmle encoded
def process_pcm_data(data, manager, Outport):

    wave_data = data
    out = io.BytesIO()
    data_ = np.frombuffer(data, dtype=np.int16)
    sv.write(out, 16000, data_)

    def buffer_generator(file):
        with wave.open(file, "rb") as f:
            frames_per_buffer = 160
            frames = f.readframes(frames_per_buffer)
            while frames:
                yield frames
                frames = f.readframes(frames_per_buffer)

    for d in buffer_generator(out):
        try:
            manager.push_data(d, finish_processing=False)
            r, r1 = manager.get_result()
            text = pretty(r)
            if text is not None:
                Outport.push(bytes(text, encoding="utf-8"), "INTERMEDIATE")
        except Exception as msg:
            log.error("Exception %s", msg)
    manager.push_data(b"", finish_processing=True)
    t = Thread(target=pusher, args=(manager, Outport), daemon=True)
    t.start()


if __name__ == "__main__":
    main()
