#!/usr/bin/python
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
 author: vinay.g@intel.com
"""
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch

# from zmq_integration_lib import InputPort, OutputPort, InputPortWithEvents
from zmq_integration_lib import get_inpad, get_outpad
import wave
import time
import sys
import os
import string
import logging as log
import numpy as np
import _config as config
log = config.get_logger()


def model_load():
    log.debug("Loading the Hugging Face Model")
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    ds = load_dataset(
        "patrickvonplaten/librispeech_asr_dummy", "clean", split="validation"
    )
    log.debug("Model is loaded succcessfully")
    return ds, processor, model


def main():
    log.info("Starting Huggingface ASR Service")
    output_addr = "ipc:///feeds/1"
    output_topic = "text"
    ooutport = get_outpad(output_addr, output_topic)

    log.info("Created Output Data Publisher")

    inputAddr = "ipc:///feeds/0"
    inputTopic = "audio"
    authzAddr = "ipc:///feeds/9"
    ippe = get_inpad(inputAddr, inputTopic, authzAddr)
    log.info("Created 0MQ Input Data Receiver")

    ds, processor, model = model_load()

    log.debug("Waiting to Receive Input Data")
    for data, event in ippe.data_and_event_generator():
        try:
            if event == "pcm":
                log.debug("Received data from Component")
                data = np.frombuffer(data, dtype=np.int16)

                # read soundfiles
                ds = ds.map(lambda x: {"speech": data})

                # process
                input_values = processor(
                    ds["speech"][0], return_tensors="pt"
                ).input_values

                # retrieve logits
                log.debug("Load data to Model")
                logits = model(input_values.float()).logits

                # take argmax and decode
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = processor.decode(predicted_ids[0])
                log.debug("Audio Transcription: {}".format(transcription))
                ds = ds.remove_columns("speech")
                log.debug("Publishing text output to 0MQ")
                ooutport.push(bytes(transcription.lower(), encoding="utf-8"), "FINAL")
        except Exception as msg:
            log.error("Received Exception %s", msg)


if __name__ == "__main__":
    main()
