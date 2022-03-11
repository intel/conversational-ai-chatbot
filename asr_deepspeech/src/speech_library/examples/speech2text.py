"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

#!/usr/bin/env python

import wave
import time
from speech_library.speech_manager import SpeechManager
import sys
from argparse import ArgumentParser, SUPPRESS


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group("Options")
    args.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="Show this help message and exit.",
    )

    args.add_argument("-i", "--input", help="Audio file.", required=True, type=str)
    args.add_argument("-c", "--config", help="Config file.", required=True, type=str)
    # args.add_argument("-o", "--out", help="Path to an output file", type=str)

    args.add_argument(
        "-d",
        "--device",
        help="Optional. Specify the target device to infer on; CPU, GPU, FPGA, HDDL, MYRIAD or HETERO: is "
        "acceptable. The sample will look for a suitable plugin for device specified. Default "
        "value is CPU",
        default="CPU",
        type=str,
    )
    return parser


def main():
    args = build_argparser().parse_args()
    input_file = args.input

    sm = SpeechManager()
    config_file = args.config

    start_time = time.time()
    sm.initialize(config_file)
    end_time = time.time()

    print("Speech manager initialized in {} secs".format(end_time - start_time))

    # output_file = args.out

    # since file is opened using "with", no need to close explicitly
    with wave.open(input_file, "rb") as f:
        try:
            data = f.readframes(-1)
        except:
            if f.closed == False:
                f.close()

    t3 = time.time()
    sm.push_data(data, finish_processing=True)
    r, r1 = sm.get_result()
    print(time.time() - t3)

    # if r1 and output_file:
    #     with open(output_file, "w") as f:
    #         f.write(r)
    # else:
    #     print("transcribed text: {}".format(r))

    if r1:
        print("transcribed text: Please uncomment the 78th line")
        # print(r)

    sm.close()


if __name__ == "__main__":
    sys.exit(main() or 0)
