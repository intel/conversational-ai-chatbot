#!/bin/sh

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause


export PYTHONPATH=$PYTHONPATH:/data
cd /app/src && rasa run actions &

#cd /app/ && rasa run --enable-api \
#                     --ssl-certificate $API_TLS_CERT \
#		     --ssl-keyfile $API_TLS_KEY \
#		     &


cd /app/ && rasa run --enable-api &
cd /app/server && python3 server.py
