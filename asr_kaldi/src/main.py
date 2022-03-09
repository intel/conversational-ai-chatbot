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
        log.info("Inferred Output: ' {} ' Final: ' {} '".format(data.decode(), Final))
    log.debug("Publishing text output to 0MQ")
    port.push(bytes(pretty(data), encoding="utf-8"), "FINAL")


def pretty(text):
    text_ = text.decode()
    return " ".join(text_.replace("<UNK>", " ").split()).lower()


def main():
    freeze_support()
    log.info("Starting Kaldi ASR Service")

    # Set Input and Output Ports
    ipp = config.get_inputport()
    log.info("Created 0MQ Input Data Receiver")

    Outport = config.get_outputport()
    log.info("Created 0MQ Output Data Publisher")

    manager = SpeechManager()
    log.debug("Speech Manager Initializing")
    config_file = "/app/src/model/speech_lib.cfg"
    manager.initialize(config_file)
    log.debug("Speech Manager Initialized")
    try:
        log.debug("Waiting to Receive Input Data")
        # Blocking Call
        for data, event in ipp.data_and_event_generator():
            log.debug(
                "Data with Length: {} is received along with event: {}".format(len(data), event)
            )
            if event == "pcm":
                log.debug("Process data received with event: {}".format(event))
                process_pcm_data(data, manager, Outport)

    except Exception as msg:
        log.error("Received Exception %s", msg)


# This function expects the data as, bytes read from a wave file.
# bitrate,16000:mono channel and pcmle encoded
def process_pcm_data(data, manager, Outport):
    log.debug("Processing data")
    wave_data = data
    out = io.BytesIO()
    data_ = np.frombuffer(data, dtype=np.int16)
    sv.write(out, 16000, data_)

    def buffer_generator(file):
        # since file is opened using "with", no need to close explicitly
        with wave.open(file, "rb") as f:
            try:
                frames_per_buffer = 160
                frames = f.readframes(frames_per_buffer)
                log.debug("Generating Frames")
                while frames:
                    yield frames
                    frames = f.readframes(frames_per_buffer)
            except Exception as msg:
                log.error("Received Exception %s", msg)
                if f.closed == False:
                    f.close()

    log.debug("Push Data to Speech Manager")
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
