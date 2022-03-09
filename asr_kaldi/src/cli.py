"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import argparse
from speech_library.speech_manager import SpeechManager
import wave
import logging

level = logging.INFO
logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=level)
logging.root.setLevel(level)
log = logging.getLogger()
log.setLevel(level)


def build_argparser():
    parser = argparse.ArgumentParser(description="Speech recognition demo")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="FILENAME",
        required=True,
        help="Path to an audio file in WAV PCM 16 kHz mono format",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="FILENAME",
        required=True,
        help="Path to config file",
    )
    return parser


def buffer_generator(file):
    # since file is opened using "with", no need to close explicitly
    with wave.open(file, "rb") as f:
        try:
            frames_per_buffer = 160
            frames = f.readframes(frames_per_buffer)
            while frames:
                yield frames
                frames = f.readframes(frames_per_buffer)
        except:
            if f.closed == False:
                f.close()


def main():
    log.info("Speech to Text with KALDI")
    args = build_argparser().parse_args()
    log.info("Initializing model")
    manager = SpeechManager()
    manager.initialize(args.config)
    log.info("Reading audio file")
    for d in buffer_generator(args.input):
        try:
            manager.push_data(d, finish_processing=False)
            r, r1 = manager.get_result()
        except Exception as msg:
            log.error(msg)
    manager.push_data(b"", finish_processing=True)

    def text_gen(manager):
        final = False
        while not final:
            data, final = manager.get_result()
            yield (data, final)

    log.info("Text Output:")
    for d, _ in text_gen(manager):
        print(d.decode().lower(), end="\r")
    print("\n")

    manager.close()


main()
