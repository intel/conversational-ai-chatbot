## Out of Scope
* out_of_scope
  - action_default_fallback
  - utter_supported

## Greetings
* greet
  - utter_greet

## User enquires about Bank information 
* getbanks
  - action_default_fallback

## User enquires about ATM information city bank 
* get_atms_for_bank
  - action_get_atms

## User enquires about account information city bank
* get_accounts_bank
  - action_list_accounts

## User enquires about balance information city bank
* get_account_info
 - action_list_account_balance


## End of Conversation:
* goodbye
  - action_logout

## bot challenge
* bot_challenge
  - utter_iamabot

## show capability
* get_capability
  - utter_iamabot
  - utter_supported


## interactive_story_1
* greet
    - utter_greet
* get_accounts_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_list_accounts
    - slot{"account_number": "1911mc10:1911mc11"}
* get_account_info_bank
    - action_list_account_balance
* goodbye
    - action_logout
* stop

## interactive_story_1
* get_accounts_bank
    - action_list_accounts
* get_accounts_bank
    - action_list_accounts
* get_accounts_bank
    - action_list_accounts

## interactive_story_1
* out_of_scope{"entity_name": "facebook"}
    - action_default_fallback
* out_of_scope{"entity_name": "twitter"}
    - action_default_fallback
* out_of_scope{"entity_name": "twitter"}
    - action_default_fallback
* out_of_scope
    - action_default_fallback
* out_of_scope
    - action_default_fallback
* greet
    - utter_greet
* out_of_scope
    - action_default_fallback
* out_of_scope{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_default_fallback
* out_of_scope
    - action_default_fallback
* get_accounts_bank
    - action_list_accounts
    - slot{"account_number": "1911mc10:1911mc11"}
* get_account_info_bank
    - action_list_account_balance
* goodbye
    - action_logout
    - slot{"account_number": null}
    - slot{"bank_name": null}

## interactive_story_1
* get_accounts_bank{"bank_name": "sbi"}
    - slot{"bank_name": "sbi"}
    - action_list_accounts
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_account_info_bank{"account_number": "1911mc10", "bank_name": "Bank-of-Pune"}
    - slot{"account_number": "1911mc10"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_list_account_balance
* greet
    - utter_greet
* get_atms_for_bank
    - action_get_atms
* get_atms_for_bank
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* out_of_scope
    - action_default_fallback
* get_atms_for_bank
    - action_get_atms
* get_atms_for_bank
    - action_get_atms
* get_atms_for_bank
    - action_get_atms
* goodbye
    - action_logout

## interactive_story_1
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
* get_accounts_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_list_accounts
* get_account_info_bank
    - action_list_account_balance
* get_atms_for_bank{"bank_name": "Bank-of-Pune"}
    - slot{"bank_name": "Bank-of-Pune"}
    - action_get_atms
