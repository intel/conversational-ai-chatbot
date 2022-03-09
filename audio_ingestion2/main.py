"""
 ReSpeaker Python Library
 Copyright (c) 2016 Seeed Technology Limited.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import logging as log
import time
from threading import Thread, Event
import wave
import io
from respeaker import Microphone
from zmq_integration_lib import OutputPort
import _config as config


log = config.get_logger()
login_watcher = config.get_login_watcher()


def publish_pcm(Outport, file):
    session_valid = login_watcher.session_valid
    log.debug("Subscribing, to get a valid Session")
    if session_valid:
        import wave

        # since file is opened using "with", no need to close explicitly
        with wave.open(io.BytesIO(file)) as f:
            try:
                data = f.readframes(-1)
                login = login_watcher.session_id
                h = Outport.update_session_id(login)
                log.debug("Publishing the Data")
                return Outport.push(data, "pcm")
            except Exception as msg:
                if f.closed == False:
                    f.close()
                log.error("Received Exception %s", msg)
    log.debug("Session Invalid")


def task(quit_event, op):
    try:
        mic = Microphone(quit_event=quit_event)
        log.debug("Microphone Initialized ")
        time = 0
        is_wakeup = False
        condition = False
        while not quit_event.is_set():
            if mic.wakeup(config.WAKE_UP_WORD):
                log.debug("Wake up word detected, Started Listening")
                data = mic.listen()
                recorded_wav = io.BytesIO()
                log.debug("Recorded Audio")

                # since file is opened using "with", no need to close explicitly
                with wave.open(recorded_wav, "wb") as wav:
                    try:
                        wav.setsampwidth(config.sample_width)
                        wav.setnchannels(config.audio_channels)
                        wav.setframerate(config.bitrate)
                        # log.debug("Configuring the Wave file with Required Dataset")
                        # wav.writeframes(frames)
                        for d in data:
                            if d:
                                wav.writeframes(d)
                    except Exception as msg:
                        log.error("Received Exception %s", msg)
                        if wav.closed == False:
                            wav.close()

                log.debug("Trying to Publish")
                publish_pcm(op, recorded_wav.getvalue())
                log.debug("Published Audio")
    except Exception as msg:
        log.error("Received Exception %s", msg)


def main():
    log.info("Audio Ingestion Service Started")
    # op = OutputPort(addr=config.OUTPUT_ADDR, topic=config.OUTPUT_TOPIC)
    Outport = config.get_output_port()
    quit_event = Event()
    thread = Thread(target=task, args=(quit_event, Outport))
    thread.start()
    log.debug("Recorder Started...")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            log.debug("Quit")
            quit_event.set()
            break
    thread.join()


if __name__ == "__main__":
    main()
