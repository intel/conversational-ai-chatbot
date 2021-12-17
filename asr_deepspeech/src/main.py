"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from speech_library.speech_manager import SpeechManager
from multiprocessing import freeze_support
import numpy as np
from zmq_integration_lib import InputPortWithEvents, OutputPort
import scipy.io.wavfile
import _config as config

log = config.get_logger()


def pusher(manager, port):
    Final = False
    data = ""
    while not Final:
        data, Final = manager.get_result()
        log.debug("Inferred Output: ' {} ' Final ' {} '".format(data, Final))
    port.push(bytes(pretty(data), encoding="utf-8"), "FINAL")


def pretty(text):
    # redundant call now, used as a placeholder for formatting
    return " ".join(text.replace("<UNK>", " ").split()).lower()


class ZMQInputPort(InputPortWithEvents):
    pass


def audio_input(bytes):
    return np.frombuffer(bytes)


def main():
    freeze_support()
    log.info("Starting Deepspeech ASR Service")

    # Set Input and Output Ports
    ipp = config.get_inputport()
    log.info("Created 0MQ Input Data Receiver")

    Outport = config.get_outputport()
    log.info("Created Output Data Publisher")

    manager = SpeechManager()
    log.debug("Speech Manager Initializing")
    config_file = "/model/deepspeech8.cfg"
    manager.initialize(config_file)
    log.debug("Speech Manager Initialized")

    try:
        log.debug("Waiting to Receive Input Data")
        for data, event in ipp.data_and_event_generator():
            log.debug("Data with Length: {} is received along with event: {}".format(len(data), event))
            if event == "pcm":
                log.debug("Process data received with event: {}".format(event))
                process_pcm_data(data, manager, Outport)
                continue
            if event == "wave_file":
                process_wave(data, manager, Outport)
                continue
            log.error("Streaming Input Support Removed")
    except Exception as msg:
        log.error("Received Exception %s", msg)
    manager.close()


def process_wave(data, manager, Outport):
    # import wave
    # b = io.BytesIO(data)
    # wave_data = scipy.io.wavfile.read(b)
    # process_wave_data(wave_data, manager, Outport)
    pass


def process_pcm_data(data, manager, Outport):
    log.debug("Processing Audio Data")
    wave_data = data
    manager.push_data(wave_data, finish_processing=True)
    r, r1 = manager.get_result()
    log.debug("Inferred Output: ' {} ' Final ' {} '".format(r, r1))
    log.debug("Publishing text output to 0MQ")
    Outport.push(bytes(r, encoding="utf-8"), "FINAL")


def process_streaming_input(data, manager, Outport):
    # TODO: This would be removed
    pass


if __name__ == "__main__":
    main()
