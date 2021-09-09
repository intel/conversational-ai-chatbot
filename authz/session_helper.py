"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import secrets
import _config as config
import time
from threading import RLock


class Session(object):
    def __init__(self, token=""):
        # Create a session ID
        self.jwt = token
        self.id = secrets.token_hex(16)
        self.expires_at = time.time() + config.SESSION_TIMEOUT_IN_SECS
        self._active = True

    def _clear_token(self):
        self.jwt = None

    @property
    def active(self):
        if time.time() > self.expires_at:
            print ("Session Timed Out")
            self._clear_token()
            return False
        return True

    def valid(self, session_id):
        while self.active:
            if not self.id == session_id:
                return False
            return True
        return False

    @property
    def token(self):
        if self.active:
            pass
        return self.jwt


# This cache can only keep valid sessions,
#
class SessionCache(dict):
    handlers = []
    lock = RLock()

    def add_session(self, session):
        with self.lock:
            if session.active:
                super().__setitem__(session.id, session)

    def empty_callback(self, handler):
        # call this callback when cache is empty
        # i.e session expires
        self.handlers.append(handler)

    def remove_entry(self, session_id):
        try:
            super().pop(session_id)
        except Exception as msg:
            log.info("Exception raised %s", msg)
        for h in self.handlers:
            h()

    def __getitem__(self, x):
        with self.lock:
            s = super().__getitem__(x)
            if s.active:
                return s
            else:
                super().pop(x)
                for h in self.handlers:
                    h(s.token)
                raise KeyError


def _test_main():
    token = "500"
    login_session = Session(token)

    session_id = login_session.id
    log.info("Session id is {}: ".format(session_id))
    session_store = SessionCache()
    session_store.add_session(login_session)

    # check for session id in store
    try:
        log.info(
            "Token Verified {}:".format(session_store[session_id].valid(session_id))
        )
        log.info(session_store[session_id].token)
    except (KeyError, IndexError):
        pass

    while login_session.active:
        log.info(session_store[session_id].token)
        time.sleep(1)

    log.info("Token Verified {}:".format(session_store[session_id].valid(session_id)))
    # After expiry we cannot get token, it will raise an exception and
    # the session will be automatically removed from the cache
    log.info(session_store[session_id].token)
    log.info(session_store.keys())


# _test_main()
