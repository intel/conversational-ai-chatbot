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
        log.info("in thread: data [ {} ] final [ {} ]".format(data, Final))
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
    log.info("main: deepspeech ASR")

    # Set Input and Output Ports
    ipp = config.get_inputport()
    Outport = config.get_outputport()

    log.info("main: Input/Output Ports set")
    manager = SpeechManager()
    config_file = "/model/deepspeech8.cfg"
    manager.initialize(config_file)
    log.info("main: Speech Manager Initialized")

    try:
        for data, event in ipp.data_and_event_generator():
            log.info("Data len: {} event : {}".format(len(data), event))
            if event == "pcm":
                process_pcm_data(data, manager, Outport)
                continue
            if event == "wave_file":
                process_wave(data, manager, Outport)
                continue
            log.error("streaming input support removed")
    except Exception as msg:
        log.info("main: Received Exception %s", mesg)
    manager.close()


def process_wave(data, manager, Outport):
    # import wave
    # b = io.BytesIO(data)
    # wave_data = scipy.io.wavfile.read(b)
    # process_wave_data(wave_data, manager, Outport)
    pass


def process_pcm_data(data, manager, Outport):
    wave_data = data
    manager.push_data(wave_data, finish_processing=True)
    r, r1 = manager.get_result()
    Outport.push(bytes(r, encoding="utf-8"), "FINAL")


def process_streaming_input(data, manager, Outport):
    # TODO: This would be removed
    pass


if __name__ == "__main__":
    main()
