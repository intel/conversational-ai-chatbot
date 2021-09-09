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
"""Helper module for managing audio devices"""
import logging
from threading import Event

import numpy as np
import soundcard

TARGET_CHANNELS = [0]
TARGET_SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = int(TARGET_SAMPLE_RATE / 1)
INT16_INFO = np.iinfo(np.int16)

_logger = logging.getLogger()


def get_input_device_list():
    """Return tuple containing:
    list of audio devices (tuples of SoundCard Device instance and name),
    index of default input device on this list,
    index of default loopback device on this list
    """
    devices = [
        (mic, mic.name) for mic in soundcard.all_microphones(include_loopback=True)
    ]
    try:
        default_output_name = soundcard.default_speaker().name
        default_loopback = next(
            (
                mic
                for mic in soundcard.all_microphones(include_loopback=True)
                if mic.isloopback and default_output_name in mic.name
            ),
            None,
        )
    except RuntimeError:
        default_loopback = None
    try:
        default_input = soundcard.default_microphone()
    except RuntimeError:
        default_input = None
    return (
        devices,
        _find_device_on_list(default_input, devices),
        _find_device_on_list(default_loopback, devices),
    )


def _find_device_on_list(device, device_list):
    """Return index of given device on the list
    :param device: SoundCard Device instance to find
    :param device_list: List of audio devices (tuples of SoundCard Device instance and name)
    """
    return next(
        (i for i, e in enumerate(device_list)
         if device and device.name == e[0].name), 0
    )


class StreamReader:
    """Class responsible for reading audio stream data from device"""

    def __init__(
        self,
        device,
        callback=None,
        clipping_callback=None,
        level_callback=None,
        volume_getter=None,
    ):
        """
        :param device: SoundCard Device
        :param callback: Audio data callback
        :param clipping_callback: Clipping callback
        :param level_callback: Audio level callback
        :param volume_getter: Volume getter
        """
        _logger.debug("Initializing StreamReader")
        self._device = device
        self._callback = callback
        self._clipping_callback = clipping_callback
        self._level_callback = level_callback
        self._volume_getter = volume_getter

        self._clipping = False
        self._stream = None
        self._stop = Event()

    def initialize(self):
        """Initialize stream reader
        :return: True if successful, False otherwise
        """
        _logger.debug("Initializing device: %s", self._device)
        self._stop.clear()
        try:
            self._stream = self._device.recorder(
                TARGET_SAMPLE_RATE, channels=TARGET_CHANNELS
            )
        except (RuntimeError, TypeError) as exc:
            _logger.error("Cannot initialize device %s. %s", self._device, exc)
            return False
        return True

    def read_stream(self):
        """Run stream reading until stop_stream() is called. Should be executed in new thread."""
        _logger.info("Stream reading started")
        try:
            with self._stream:
                while not self._stop.is_set():
                    np_data = self._stream.record(FRAMES_PER_BUFFER)
                    np_data = self._scale_volume(np_data)
                    self._calculate_level(np_data)
                    self._detect_clipping(np_data)
                    frames = np.ndarray.tostring(np_data.astype(np.int16))
                    if self._callback:
                        self._callback(frames)
        except RuntimeError as exc:
            _logger.error("Cannot read from device %s. %s", self._device, exc)
        _logger.info("Stream reading finished")

    def stop_stream(self):
        """Stop stream reading"""
        self._stop.set()
        if self._stream:
            self._stream.flush()

    def _scale_volume(self, np_data):
        """Multiply input data by current volume and clip to int16 range
        :param np_data: Numpy array
        :return: Multiplied array
        """
        volume = 1  # by default volume is at 100%
        if self._volume_getter:
            volume = self._volume_getter()
        # scale from float [-1, 1] to int16 range
        np_data *= volume * INT16_INFO.max
        if volume != 1:
            np.clip(np_data, INT16_INFO.min, INT16_INFO.max, np_data)
        return np_data

    def _calculate_level(self, np_data):
        """Calculate audio level and pass it to callback function as float [0, 1]
        :param np_data: Numpy array
        """
        if self._level_callback:
            level = max(np_data.max(), abs(np_data.min())) / INT16_INFO.max
            self._level_callback(level)

    def _detect_clipping(self, np_data):
        """Check if clipping occurred and execute callback function if needed
        :param np_data: Numpy array
        """
        for sample in np_data:
            if sample in (INT16_INFO.min, INT16_INFO.max):
                if self._clipping:
                    _logger.warning("Clipping detected")
                    if self._clipping_callback:
                        self._clipping_callback()
                    break
                self._clipping = True
            else:
                self._clipping = False
