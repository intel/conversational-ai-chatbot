"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import time
import signal
import time
import _config as config

log = config.get_logger()
login_watcher = config.get_login_watcher()

# Since this component recieves session_id from authz, only this component needs to update session id for the output port.
def publish_pcm(Outport, file):
    session_valid = login_watcher.session_valid
    log.debug("Checking Valid Session")
    if session_valid:
        import wave

        log.debug("Reading/Opening the wave file ")
        # since file is opened using "with", no need to close explicitly
        with wave.open(file) as f:
            try:
                data = f.readframes(-1)
                Outport.update_session_id(login_watcher.session_id)
                log.debug("Publishing the Data using 0MQ ")
                return Outport.push(data, "pcm")
            except:
                if f.closed == False:
                    f.close()
    log.debug("Session Invalid")


class ExitHandler(object):
    ExitNow = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signal_num, frame):
        log.debug("Caught signal. Ready to Exit ")
        self.ExitNow = True


def main():

    # EH Catches signals and updates state. Used to stop and join threads.
    log.info("Audio Ingestion Service Started")
    EH = ExitHandler()

    Outport = config.get_output_port()
    log.info("Created Output Data Publisher")

    if config.WAVE_PATH:
        log.info("Publishing wave file as wave path is provided")
        # TODO: infinite looping is for testing, read an env variabel to set number of times to loop

        log.debug("Checking Active Session")
        while not login_watcher.session_valid:
            # wait
            time.sleep(2)
        Loop = True
        log.debug("Valid Session is in Progress")
        log.debug("Starting Wave Ingestion")
        while Loop:
            time.sleep(10)
            for wfile in config.get_wave_files():
                try:
                    publish_pcm(Outport, wfile)
                    audio_file = wfile.rsplit("/", 1)[1]
                    log.debug("publishing {}".format(audio_file))
                    time.sleep(30)
                except Exception as msg:
                    log.error("Received Exception %s", msg)


if __name__ == "__main__":
    main()
