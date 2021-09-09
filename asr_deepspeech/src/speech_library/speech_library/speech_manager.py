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
"""Speech Library Manager module"""
import logging
import logging.handlers
import threading
from multiprocessing import Process, Pipe, Queue

from speech_library.speech_proxy import speech_process

_logger = logging.getLogger()


class SpeechManager:
    """Speech Library Manager"""

    def __init__(self):
        self._parent_conn, self._child_conn = Pipe()
        self._process = None

    def initialize(self, asr_config, **kwargs):
        """Initialize
        :param asr_config: Path to configuration file
        :param kwargs: Keyword arguments (batch_size, infer_device)
        :return: True if successful, False otherwise
        """
        logger_queue = Queue()
        logger_thread = threading.Thread(
            target=_log_handler, args=(logger_queue,), daemon=True
        )
        logger_thread.start()

        self._process = Process(
            target=speech_process,
            args=(self._child_conn, logger_queue, asr_config),
            kwargs=kwargs,
        )
        self._process.start()

        if self._parent_conn.recv()[0] is None:
            _logger.error("Failed to initialize Speech Library process")
            self._process.join()
            return False
        return True

    def push_data(self, wave_data, finish_processing=False):
        """Push audio data to Speech Library
        :param wave_data: Audio data to push (bytes)
        :param finish_processing: Finish processing if True
        """
        self._parent_conn.send((wave_data, finish_processing))

    def get_result(self):
        """Get result text from Speech Library
        :return: Tuple of result text (bytes) and True if result is stable, False otherwise
        """
        utt_text, is_stable = self._parent_conn.recv()
        return utt_text, is_stable

    def close(self):
        """Release Speech Library handle"""
        self._parent_conn.send((None, None))
        self._process.join()


def _log_handler(logger_queue):
    """Handle logger messages from Speech Library process
    :param logger_queue: Logger queue
    """
    while True:
        record = logger_queue.get()
        if record is None:
            break
        logger_ = logging.getLogger(record.name)
        logger_.handle(record)
