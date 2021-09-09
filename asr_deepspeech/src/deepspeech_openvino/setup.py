"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from setuptools import setup

setup(
    name="deepspeech_openvino",
    version="1.0",
    install_requires=[
        "librosa",
        "numpy",
        "ctcdecode_numpy",
    ],
    packages=["deepspeech_openvino", "deepspeech_openvino.utils"],
)
