"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from obp_api.base import apiObject


class Bank(apiObject):
    def create_bank(self):
        pass

    def create_transaction_type_at_bank(self):
        pass

    def get_bank(self):
        pass

    def get_banks(self):
        cmd = "get"
        endpoint = "/obp/v4.0.0/banks"
        response = self.request(cmd, endpoint)
        if response.ok:
            js = response.json()
            list_of_banks = js["banks"]
            return list_of_banks

    def get_transaction_types_at_bank(self):
        pass


class Branch(apiObject):
    def create_branch(self):
        pass

    def delete_branch(self):
        pass

    def get_branch(self):
        pass

    def get_branches_for_bank(self):
        pass
