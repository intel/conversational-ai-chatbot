#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation

It is based on https://github.com/openvinotoolkit/open_model_zoo/blob/master/demos/speech_recognition_demo/python
"""
from deepspeech_openvino.deepspeech_asr_v8 import DeepSpeechv8
import wave
import argparse


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
        "-d",
        "--device",
        default="CPU",
        type=str,
        help="Optional. Specify the target device to infer on, for example: CPU, GPU, FPGA, HDDL, MYRIAD or HETERO. "
        "The sample will look for a suitable IE plugin for this device. (default is CPU)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        metavar="FILENAME",
        required=True,
        help="Path to an .xml file with a trained model (required)",
    )
    parser.add_argument(
        "-c",
        "--alphabet_cfg",
        type=str,
        metavar="FILENAME",
        required=True,
        help="Path to an alphabet_cfg (required)",
    )
    parser.add_argument(
        "-L",
        "--lm",
        type=str,
        metavar="FILENAME",
        help="path to language model file (optional)",
    )
    return parser


def read_wave_to_buffer(wavefile):
    # since file is opened using "with", no need to close explicitly
    with wave.open(args.input, "rb") as wave_read:
        try:
            (
                channel_num,
                sample_width,
                sampling_rate,
                pcm_length,
                compression_type,
                _,
            ) = wave_read.getparams()
            assert sample_width == 2, "Only 16-bit WAV PCM supported"
            assert compression_type == "NONE", "Only linear PCM WAV files supported"
            assert channel_num == 1, "Only mono WAV PCM supported"
            audio = np.frombuffer(
                wave_read.readframes(pcm_length * channel_num), dtype=np.int16
            ).reshape((pcm_length, channel_num))
            return audio
        except:
            if wave_read.closed == False:
                wave_read.close()


def main():
    args = build_argparser().parse_args()
    ts = DeepSpeechv8(
        model=args.model,
        device=args.device,
        alphabet_cfg=alphabet_cfg,
        sample_rate=16000,
        lang_model=lm,
    )
    buf = read_wave_to_buffer(wavefile)
    ts.push_data(buf)
    res = ts.get_result(True, True)
    print("{}".format(res))
    ts.close()


if "__name__" == "__main__":
    main()
