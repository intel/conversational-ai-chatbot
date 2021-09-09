"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from setuptools import setup

setup(
    name="speech_library",
    version="1.0",
    install_requires=[
        "deepspeech_openvino",
        "asr",
    ],
    packages=["speech_library"],
)
