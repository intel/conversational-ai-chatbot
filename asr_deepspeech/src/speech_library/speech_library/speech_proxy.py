# *****************************************************************************
# Copyright (C) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#
#
# SPDX-License-Identifier: Apache-2.0
# *****************************************************************************
"""ASR Proxy module"""
import logging
import logging.handlers
import os
from asr.transcriber import SpeechTranscriber

SPEECH_LIB_PATH = os.path.join(
    os.path.join(os.path.dirname(os.getcwd()), "lib"))
SPEECH_CONFIG = "speech_lib.cfg"

_logger = logging.getLogger()


class SpeechProxy:
    """ "Proxy for ASR process"""

    def __init__(self, logger_queue):
        """
        :param logger_queue: Queue for passing logger messages to main process
        """
        self._speech = None
        self._logger_queue = logger_queue
        queue_handler = logging.handlers.QueueHandler(self._logger_queue)
        _logger.setLevel(logging.INFO)
        _logger.addHandler(queue_handler)
        _logger.debug("Initialized SpeechProxy")

    def initialize(self, asr_config, **kwargs):
        """Initialize ASR
        :param asr_config: Path to configuration file
        :param kwargs: Keyword arguments (batch_size, infer_device)
        :return: True if successful, False otherwise
        """
        self._speech = SpeechTranscriber(SPEECH_LIB_PATH)
        res = False
        try:
            res = self._speech.initialize(asr_config, **kwargs)
        except Exception:
            _logger.error("Speechproxy failed to initialize()")
        return res == True

    def push_data(self, wave_data):
        """Push audio data to ASR
        :param wave_data: Audio data to push (bytes)
        :return: True if result is stable, False otherwise
        """
        if self._speech:
            return self._speech.push_data(wave_data)
        return False

    def get_result(self, final=False, finish_processing=False):
        """Get result text from ASR
        :param final: Get final result if True, preview result otherwise
        :param finish_processing: Process residue data if True
        :return: Result text (bytes)
        """
        if self._speech:
            return self._speech.get_result(
                final=final, finish_processing=finish_processing
            )
        return b""

    def close(self):
        """Release ASR handle"""
        self._logger_queue.put(None)
        if self._speech:
            self._speech.close()
        self._speech = None


def speech_process(conn, logger_queue, asr_config, **kwargs):
    """ASR processing loop
    :param conn: Communication pipe connection
    :param logger_queue: Logger queue
    :param asr_config: Path to configuration file
    :param kwargs: Initialization keyword arguments (batch_size, infer_device)
    """
    speech = SpeechProxy(logger_queue)
    if not speech.initialize(asr_config, **kwargs):
        _logger.error("Failed to initialize ASR recognizer")
        conn.send((None, None))
        speech.close()
        return
    conn.send((b"", False))
    while True:
        data_in, finish_processing = conn.recv()
        if data_in is None:
            speech.close()
            break
        is_stable = speech.push_data(data_in) if data_in else False
        try:
            utt_text = speech.get_result(
                final=is_stable or finish_processing,
                finish_processing=finish_processing,
            )
            conn.send((utt_text, is_stable or finish_processing))
        except Exception as msg:
            print("speech_process: exception: %s" % msg)
