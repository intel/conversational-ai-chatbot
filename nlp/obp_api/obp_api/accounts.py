"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from obp_api.base import apiObject


class Account(apiObject):
    def check_available_funds(self):
        pass

    def create_account(self):
        cmd = "put"
        pass

    def create_account_post(self):
        pass

    def create_account_attribute(self):
        pass

    def create_account_attribute_definition(self):
        pass

    def delete_account_aatribute_definition(self):
        pass

    def get_account_attribute_definition(self):
        pass

    def get_account_by_id(self, BANK_ID, ACCOUNT_ID):
        cmd = "get"
        endpoint = "/obp/v4.0.0/my/banks/{0}/accounts/{1}/account".format(
            BANK_ID, ACCOUNT_ID
        )
        response = self.request(cmd, endpoint)
        if response.ok:
            try:
                js = response.json()
                return js
            except Exception:
                return {}

    def get_account_by_id_full(self):
        pass

    def get_account_balances(self):
        pass

    def get_accounts_held(self, BANK_ID):
        cmd = "get"
        endpoint = "/obp/v4.0.0/banks/{0}/accounts-held".format(BANK_ID)
        response = self.request(cmd, endpoint)
        if response.ok:
            try:
                js = response.json()["accounts"]
                return js
            except Exception:
                return []

    def get_ids_of_accounts_at_bank(self):
        pass

    def get_accounts_at_bank_minimal(self):
        pass

    def get_accounts_at_bank(self):
        pass

    def get_accounts_at_all_banks_private(self):
        pass

    def get_checkbook_orders(self):
        pass

    def get_firehose_accounts_at_bank(self):
        pass

    def update_account_attribute(self):
        pass

    def update_account_label(self):
        pass

    def update_account(self):
        pass
