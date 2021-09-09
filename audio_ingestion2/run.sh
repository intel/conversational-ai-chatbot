#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

export PYTHONPATH=$PYTHONPATH:/app/respeaker_python_library
cd respeaker_python_library/examples/ && python3 main.py

