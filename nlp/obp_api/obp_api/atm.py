"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from obp_api.base import apiObject

# ATM
# Create ATM
# Get Bank ATM
# Get Bank ATMS


class ATM(apiObject):
    def create(self, bank, atm):
        cmd = "post"
        endpoint = "/obp/v4.0.0/banks/{0}/atms"
        # payload = {  "id":"atm-id-123",  "bank_id":"gh.29.uk",  "name":"Atm by the Lake",  "address":{    "line_1":"No 1 the Road",    "line_2":"The Place",    "line_3":"The Hill",    "city":"Berlin",    "county":"",    "state":"Brandenburg",    "postcode":"13359",    "country_code":"DE"  },  "location":{    "latitude":11.45,    "longitude":11.45  },  "meta":{    "license":{      "id":"5",      "name":"TESOBE"    }  },  "monday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "tuesday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "wednesday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "thursday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "friday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "saturday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "sunday":{    "opening_time":"10:00",    "closing_time":"18:00"  },  "is_accessible":"true",  "located_at":"Full service store",  "more_info":"short walk to the lake from here",  "has_deposit_capability":"true"}

    def get_atm(self, BANK_ID, ATM_ID):
        cmd = "get"
        endpoint = "/obp/v4.0.0/banks/{0}/atms/{1}".format(BANK_ID, ATM_ID)
        response = self.request(cmd, endpoint)
        if response.ok:
            try:
                return response.json()["atms"]
            except Exception:
                return []

    def get_bank_atms(self, BANK_ID):
        cmd = "get"
        endpoint = "/obp/v4.0.0/banks/{0}/atms".format(BANK_ID)
        response = self.request(cmd, endpoint)
        try:
            return response.json()["atms"]
        except Exception:
            return []
