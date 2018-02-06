from Libraries.Account import Account
from Libraries.CF import CF

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_account(event, context):
    account = Account(event.username, event.password, event.api_signature, event.account_type)
    cf = CF(event.stack_name)

    # Get current balance of account
    account_balance = account.get_balance()

    # Calculate the hourly cost of the CF template
    cf_hourly_cost = cf.get_cost()

    # Make CF start/stop/modify decision
    cf_action = cf.make_decision(account_balance)

    if cf_action == 'stay':
        message = "Given the account balance of %f.2 and an hourly cost of %f.2, it was decided to not change anything." % \
                    (account_balance, cf_hourly_cost)
    else:
        message = "Given the account balance of %f.2 and an hourly cost of %f.2, it was decided to %s." % \
                    (account_balance, cf_hourly_cost, cf_action)

    logger.info(message)