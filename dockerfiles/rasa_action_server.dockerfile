# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

FROM rasa:1.10.1
LABEL maintainer Shivdeep Singh <shivdeep.singh@intel.com>

COPY nlp/obp_api /data/obp_api
RUN cd /data/obp_api \
    && python setup.py install
COPY nlp/rasa_actions_server/src /app/src
COPY nlp/rasa_actions_server/run.sh /app/run.sh

RUN mkdir -p /app
COPY nlp/rasa_api_server/ /app/
COPY nlp/nlp_server /app/server
# train model
RUN cd /app && rasa train --force 

# Install integration lib
COPY integration_library /tmp/integration_library
RUN cd /tmp/integration_library/zmq_integration_lib \
    && bash install.sh
# Run both action and api server
COPY dockerfiles/create_user.sh /create_user.sh
RUN chmod a+x /create_user.sh \
     && /create_user.sh \
     && rm /create_user.sh \
     && usermod -aG audio sys-admin
USER sys-admin
CMD ["/app/run.sh"]
