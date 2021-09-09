#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from session_helper import Session, SessionCache
import _config as config
from threading import Thread
import time

log = config.get_logger()
publisher = config.get_session_publish_port()


session_store = {}


def verify(session_id):
    try:
        return session_store[session_id].valid(session_id)
    except Exception:
        return False


def get_token():
    token = None
    try:
        session_id = list(session_store.keys())[0]
        token = session_store[session_id].token
        return token
    except Exception as msg:
        log.info(msg)
    return token


def logout(token):
    log.info("Logout")
    try:
        session_id = list(session_store.keys())[0]
        session_store.remove_entry(session_id)
    except Exception as msg:
        log.info("Exception raised {}".format(msg))
    config.logout(token)
    return True


def start_rpc_server():
    verifier = config.get_verfier_server()
    verifier.set_handler("verify", verify)
    verifier.run()


def start_token_server():
    token_server = config.get_token_server()
    token_server.set_handler("get_token", get_token)
    token_server.set_handler("logout", logout)
    token_server.run()


def start_servers():
    rpc = Thread(target=start_rpc_server, daemon=True)
    rpc.start()
    token_rpc = Thread(target=start_token_server, daemon=True)
    token_rpc.start()


def session_id_publisher():
    import time

    while True:
        try:
            session_id = list(session_store.keys())[0]
            if verify(session_id):
                config.session_publish(publisher, session_id, "signin")
            time.sleep(2)
        except (KeyError, IndexError):
            # TODO: it doesn't work properly
            config.session_publish(publisher, session_id, "signout")


def create_login_session(old_token=None):
    if old_token:
        logout(old_token)
    log.info("Create Login")
    global session_store
    login_token = config.get_login_token()
    login_session = Session(login_token)
    # log.info ('session-d {}'.format(login_session.id))
    session_store.add_session(login_session)


def main():
    global session_store
    session_store = SessionCache()
    create_login_session()
    session_store.empty_callback(create_login_session)
    start_servers()
    tm = Thread(target=session_id_publisher, daemon=True)
    tm.start()

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()
