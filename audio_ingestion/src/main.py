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
    if session_valid:
        import wave

        with wave.open(file) as f:
            data = f.readframes(-1)
            Outport.update_session_id(login_watcher.session_id)
            return Outport.push(data, "pcm")


class ExitHandler(object):
    ExitNow = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signal_num, frame):
        log.info("Caught signal. Ready to Exit ")
        self.ExitNow = True


def main():

    # EH Catches signals and updates state. Used to stop and join threads.
    EH = ExitHandler()

    log.info("Audio Ingestion")
    log.info("Started App")
    Outport = config.get_output_port()

    if config.WAVE_PATH:
        log.info("Publishing wave file as wave path is provided")
        # TODO: infinite looping is for testing, read an env variabel to set number of times to loop

        while not login_watcher.session_valid:
            # wait
            time.sleep(2)
        Loop = True
        while Loop:
            time.sleep(10)
            log.info("Publishing File ")
            for wfile in config.get_wave_files():
                publish_pcm(Outport, wfile)
                time.sleep(30)


if __name__ == "__main__":
    main()
