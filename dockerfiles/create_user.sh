#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

# create a user group
USER=sys-admin
UUID=800
GROUP=chatbot
GID=1102

echo -e "\n\n" | adduser $USER
# create a user group
usermod -u $UUID $USER
groupadd -g $GID $GROUP

usermod -a -G $GROUP $USER
# set default gid
usermod -g $GROUP $USER
