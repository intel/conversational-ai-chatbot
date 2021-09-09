"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from obp_api import atm, banks, accounts
from obp_api import base
from rasa_sdk.events import SlotSet

import logging as log
import zmq_integration_lib as z
import os


def get_jwt():
    c = z.RPCClient(os.environ["TOKEN_SERVER_ADDR"], z.supported_cmds)
    return c.get_token()


def logout(token):
    c = z.RPCClient(os.environ["TOKEN_SERVER_ADDR"], z.supported_cmds)
    return c.logout(token)

level = logging.ERROR
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=level)
logging.root.setLevel(level)
logger = logging.getLogger()
logger.setLevel(level)
cert = None

# Set bank name alias here
# It can convert bank ID to a name


def proper_bank_name(bank_id):
    alias_store = {
        "Bank-of-Pune": "City Bank",
    }
    try:
        return alias_store[bank_id]
    except (KeyError, IndexError):
        return bank_id


def get_cert():
    global cert
    if not cert:
        try:
            cert = (
                os.path.join("/run/secrets", os.environ["ACTION_TLS_CERT"]),
                os.path.join("/run/secrets", os.environ["ACTION_TLS_KEY"]),
            )
        except (KeyError, IndexError):
            log.debug("Env vars missing: ACTION_TLS_KEY, ACTION_TLS_CERT")
    return cert


def backend_helper():
    try:
        log.info("proxy ".format(os.environ["http_proxy"]))
    except (KeyError, IndexError):
        log.info("proxy not found")
    connection_helper = base.Connector(cert=get_cert())
    connection_helper.BASE_URL = "https://apisandbox.openbankproject.com"
    connection_helper.TOKEN = get_jwt()
    return connection_helper


class ActionGetBanks(Action):
    def name(self) -> Text:
        return "action_get_banks"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print(self.name())
        log.info("Action Called {}".format(self.name()))
        conn = backend_helper()
        bank_ = banks.Bank(conn)
        list_of_banks = bank_.get_banks()
        # log.info("{}".format(list_of_banks))
        try:
            def names(x): return "  {0}".format(x["full_name"])
            banknames = map(names, list_of_banks)
            list_banks = list(banknames)
            log.info("".format(list_banks))
            texti = "\n".join(list_banks[1:5])
        except (KeyError, IndexError):
            texti = "Could not get bank list"
        dispatcher.utter_message(text=texti)

        return []


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_default")

        # Revert user message which led to fallback.
        return []


class ActionListBanks(Action):
    def name(self) -> Text:
        return "action_list_banks"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        log.info("Action Called {}".format(self.name()))

        supported_bank = "Bank-of-Pune"
        # print ("Default bank_name ", tracker.get_slot('bank_name'))
        dispatcher.utter_message(
            template="utter_supported_banks", bank_name=proper_bank_name(supported_bank)
        )
        return []


class ActionListAtms(Action):
    def name(self) -> Text:
        return "action_get_atms"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        log.info("Action Called {}".format(self.name()))
        # Get bank from tracker
        bank_name = tracker.get_slot("bank_name")
        supported_banks = ["Bank-of-Pune"]
        if not bank_name or bank_name not in supported_banks:
            dispatcher.utter_message(
                template="utter_supported_banks",
                bank_name=",".join(
                    list(map(proper_bank_name, supported_banks))),
            )
            return []
        conn = backend_helper()
        atm_ = atm.ATM(conn)
        list_of_atms = atm_.get_bank_atms(bank_name)
        # print (list_of_atms)
        # log.info("bank_name {0} , list_of_atms {1}".format(bank_name, list_of_atms))
        # names = lambda x: "  {0}".format(x['full_name'])
        # banknames = map(names, list_of_atms)
        # texti =  '\n'.join(list(banknames))
        try:
            atm_response = "you will find one near {}".format(
                list_of_atms[0]["address"]["line_1"]
            )
        except (KeyError, IndexError):
            atm_response = "No atms found for {}".format(
                proper_bank_name(bank_name))

        dispatcher.utter_message(text=atm_response)

        return []


class ActionListAccountsAtBank(Action):
    def name(self) -> Text:
        return "action_list_accounts"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get bank from tracker
        log.info("Action Called {}".format(self.name()))

        conn = backend_helper()
        atm_ = accounts.Account(conn)

        try:
            bank_name = tracker.get_slot("bank_name")
            log.info("Bank name from tracker {}".format(bank_name))
        except Exception:
            log.info("Bank name not in tracker")

        # Check unsupported banks here
        supported_banks = ["Bank-of-Pune"]
        if bank_name not in supported_banks:
            dispatcher.utter_message(
                template="utter_supported_banks",
                bank_name=",".join(
                    list(map(proper_bank_name, supported_banks))),
            )
            return []

        list_of_accounts = atm_.get_accounts_held(bank_name)
        if list_of_accounts is None:
            texti = "No account found for bank: {}".format(proper_bank_name(bank_name))
            dispatcher.utter_message(text=texti)
            return []

        def names(x): return "{0}".format(x["id"])
        # log.info("list of accounts {}".format(list_of_accounts))
        account_number = None
        total_accounts = len(list_of_accounts)
        textp = "You have {} savings accounts with our bank.".format(
            total_accounts)
        try:
            accountnames = map(names, list_of_accounts)
            texti = "\n".join(list(accountnames))
            account_number = texti.split("\n")[0]
            # log.info("Set slot: {}".format(account_number))
        except Exception:
            texti = "No account found for bank: {}".format(proper_bank_name(bank_name))
        dispatcher.utter_message(text=textp)

        account_names = map(names, list_of_accounts)
        # print (account_names)
        return [SlotSet(key="account_number", value=":".join(list(account_names)))]


class ActionListAccountBalance(Action):
    def name(self) -> Text:
        return "action_list_account_balance"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        log.info("Action Called {}".format(self.name()))

        # Get slot information from tracker
        # if slots are not filled, fallback to default reply or other replies
        # asking for slots
        account_numbers = tracker.get_slot("account_number")
        if not account_numbers:
            # go for fallback reply
            bank_name_ = tracker.get_slot("bank_name")
            dispatcher.utter_message(
                template="utter_insufficient_info_account",
                bank_name=proper_bank_name(bank_name_),
            )
            return []

        account_numbers = tracker.get_slot("account_number").split(":")
        bank_name = tracker.get_slot("bank_name")

        conn = backend_helper()

        def get_account_info(conn, bank_name, account_id):
            # log.info("Bank: {0} AccountNumber: {1}".format(bank_name, account_id))

            atm_ = accounts.Account(conn)
            list_of_accounts = atm_.get_account_by_id(bank_name, account_id)
            # log.info (list_of_accounts)
            try:
                names = list_of_accounts["balance"]
                # accountnames = map(names, list_of_accounts)
                currency_d = {"INR": "Rupees", "EUR": "EURO"}
                texti = "{0} {1}".format(
                    names["amount"], currency_d[names["currency"]])
            except Exception as msg:
                print("Got an exception ", msg)
                texti = "Sorry Couldn't get balance"
            list_of_accounts = atm_.get_account_by_id(bank_name, account_id)
            if list_of_accounts is not None:
                return (str(list_of_accounts["number"])[-4:], texti)
            return (None, None)

        # print (account_numbers)
        for ac in account_numbers:
            num, amt = get_account_info(conn, bank_name, ac)
            texti = "Balance for account ending with {} is {}".format(num, amt)
            dispatcher.utter_message(text=texti)

        return []


class ActionLogout(Action):
    def name(self) -> Text:
        return "action_logout"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        log.info("Action Called {}".format(self.name()))
        logout(get_jwt())

        # Clear slots from tracker
        dispatcher.utter_message(template="utter_goodbye")

        return [
            SlotSet(key="account_number", value=None),
            SlotSet(key="bank_name", value=None),
        ]
