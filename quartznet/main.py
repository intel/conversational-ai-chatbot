# import soundfile as sf
from zmq_integration_lib import get_inpad, get_outpad
import wave
import time
import sys
import os
import logging

inputAddr = "ipc:///feeds/0"
inputTopic = "audio"
authzAddr = "ipc:///feeds/9"
ippe = get_inpad(inputAddr, inputTopic, authzAddr)
print("Quartznet ASR: Input port set")

output_addr = "ipc:///feeds/1"
output_topic = "text"
ooutport = get_outpad(output_addr, output_topic)
print("Quartznet: Output port set")

sys.path.insert(
    0,
    "/opt/intel/openvino_2021/deployment_tools/open_model_zoo/demos/speech_recognition_quartznet_demo/python/",
)
from speech_recognition_quartznet_demo_mod import main

try:
    print("Waiting to Receive Input Data")
    for data, event in ippe.data_and_event_generator():
        if event == "pcm":
            # since file is opened using "with", no need to close explicitly
            with wave.open("/home/sys-admin/recorded.wav", "wb") as f:
                try:
                    f.setframerate(16000)
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.writeframes(data)
                except:
                    if f.closed == False:
                        f.close()
            data = None
            transcript = main(
                "/Models/quartznet-15x5-en.xml", "/home/sys-admin/recorded.wav"
            )

            # transcript = main("/home/openvino/tmp/model/public/quartznet-15x5-en/FP32/quartznet-15x5-en.xml", "/home/sys-admin/recorded.wav")

            ooutport.push(bytes(transcript, encoding="utf-8"), "FINAL")

            os.remove("/home/sys-admin/recorded.wav")
            print("Quartznet infered output:")
            print(transcript)
            sys.stdout.flush()
except Exception as e:
    print(e)
