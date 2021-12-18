#!/bin/sh

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause


export PYTHONPATH=$PYTHONPATH:/data
echo "Start RASA Action Server"
cd /app/src && rasa run actions &
echo "RASA Action Server Started"

#cd /app/ && rasa run --enable-api \
#                     --ssl-certificate $API_TLS_CERT \
#		     --ssl-keyfile $API_TLS_KEY \
#		     &

echo "Start RASA API Server"
cd /app/ && rasa run --enable-api &
echo "RASA API Server Started"

echo "Start NLP Server"
cd /app/server && python3 server.py
echo "NLP Server Started"
