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
"""Helper module for reading WAVE files"""
import audioop
import logging
import wave

TARGET_CHANNEL_COUNT = 1
TARGET_SAMPLE_RATE = 16000
SUPPORTED_SAMPLE_WIDTH = 2  # int16

_logger = logging.getLogger()


def data_generator(wave_path, buffers_per_second=1):
    """Generate data from WAVE file
    :param wave_path: Path to WAVE file
    :param buffers_per_second: How many data chunks should be yielded per second of recording
    :return: Chunk of data as bytes
    """
    # since file is opened using "with", no need to close explicitly
    with wave.open(wave_path, "rb") as file:
        try:
            if file.getnframes() <= 0:
                _logger.error("No samples to process")
                return
            sample_rate = file.getframerate()
            channel_count = file.getnchannels()
            frames_per_buffer = sample_rate // buffers_per_second
            resampler_state = None

            frames = file.readframes(frames_per_buffer)
            while frames:
                frames, resampler_state = _resample_frames(
                    frames, channel_count, sample_rate, resampler_state
                )
                yield frames
                frames = file.readframes(frames_per_buffer)
        except Exception as msg:
            _logger.error("Received Exception %s", msg)
            if file.closed == False:
                file.close()


def _resample_frames(frames, channel_count, sample_rate, resampler_state=None):
    """Resample given data frames to target sample rate
    :param frames: Input data (bytes)
    :param channel_count: Number of channels in input data
    :param sample_rate: Sample rate of input data
    :param resampler_state: Previous state of the resampler
    :return: Tuple of resampled frames and new resampler state
    """
    if channel_count > TARGET_CHANNEL_COUNT:
        frames = audioop.tomono(frames, SUPPORTED_SAMPLE_WIDTH, 1, 0)
    if sample_rate != TARGET_SAMPLE_RATE:
        frames, resampler_state = audioop.ratecv(
            frames,
            SUPPORTED_SAMPLE_WIDTH,
            TARGET_CHANNEL_COUNT,
            sample_rate,
            TARGET_SAMPLE_RATE,
            resampler_state,
        )
    return frames, resampler_state


def check_wave_format(wave_path):
    """Check if format of the given WAVE is supported (16-bit)
    :param wave_path: Path to WAVE file
    :return: True format is supported, False otherwise
    """

    # since file is opened using "with", no need to close explicitly
    with wave.open(wave_path, "r") as file:
        try:
            return file.getsampwidth() == SUPPORTED_SAMPLE_WIDTH
        except wave.Error:
            if file.closed == False:
                file.close()
            return False
