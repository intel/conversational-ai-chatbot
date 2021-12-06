#!/usr/bin/python
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
 author: vinay.g@intel.com
"""
from transformers import  Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch
#from zmq_integration_lib import InputPort, OutputPort, InputPortWithEvents
from zmq_integration_lib import get_inpad, get_outpad
import wave
import time
import sys
import os
import string
import logging as log 
import numpy as np 


def model_load():
    processor =  Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    ds = load_dataset("patrickvonplaten/librispeech_asr_dummy", "clean", split="validation")
    log.info('Model is loaded')
    return ds, processor, model

    
def main():
    output_addr="ipc:///feeds/1"
    output_topic="text"
    ooutport = get_outpad(output_addr, output_topic)

    log.info('Huggingface ASR: Output port set')

    inputAddr = "ipc:///feeds/0"
    inputTopic = "audio"
    authzAddr = "ipc:///feeds/9"
    ippe = get_inpad(inputAddr, inputTopic, authzAddr)
    log.info('Huggingface: Input port set')

    ds, processor, model = model_load()
    
    
    for data, event in ippe.data_and_event_generator():
        if event == 'pcm':
            log.info('PCM data received')
            data = np.frombuffer(data, dtype=np.int16)
             
            # read soundfiles
            ds = ds.map(lambda x: {"speech":data})
    
            # process
            input_values = processor(ds["speech"][0], return_tensors="pt").input_values

            # retrieve logits
            logits = model(input_values.float()).logits

            # take argmax and decode
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.decode(predicted_ids[0])
            print(transcription)
            ds = ds.remove_columns("speech") 
            ooutport.push(bytes(transcription.lower(), encoding='utf-8'), "FINAL")

if __name__ == "__main__":
    main()
