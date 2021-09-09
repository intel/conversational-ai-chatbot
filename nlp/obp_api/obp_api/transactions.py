"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from obp_api.base import apiObject


class Transaction(apiObject):
    def create_transaction_attribute(self):
        pass

    def update_transaction_attitude_definition(self):
        pass

    def delete_transaction_attitude_definition(self):
        pass

    def get_firehose_transactions_for_account(self):
        pass

    def get_other_account_of_transaction(self):
        pass

    def get_transaction_attribute_by_id(self):
        pass

    def get_transaction_attribute_definition(self):
        pass

    def get_transaction_attributes(self):
        pass

    def get_transaction_by_id(self):
        pass

    def get_transactions_for_account(self):
        pass

    def get_transactions_for_accoutn_full(self):
        pass

    def update_transaction_attribute(self):
        pass
