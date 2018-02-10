try:
    import unzip_requirements
except ImportError:
    pass

from libraries.accounts import Accounts
from libraries.cf import CF
from libraries.website import Website

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

website = Website()


def check_account(event, context):
    margin = int(os.environ['MARGIN'])

    accounts = Accounts()
    cf = CF(os.environ['STACK_NAME'], margin)

    # Get current balance of account
    account_balance = accounts.get_balance()

    # Calculate the hourly cost of the CF template
    cf_hourly_cost = cf.get_cost()

    # Get current state of CF template
    cf_running = cf.running()

    # Make CF start/stop/modify decision
    cf_action = cf.make_decision(account_balance)

    if cf_action == 'stay':
        message = "Given the account balance of $%.2f and an hourly cost of $%.2f and a margin of %d hours, it was decided to not change anything." % \
                    (account_balance, cf_hourly_cost, margin)
    else:
        message = "Given the account balance of $%.2f and an hourly cost of $%.2f and a margin of %d hours, it was decided to %s the cloudformation template." % \
                    (account_balance, cf_hourly_cost, margin, cf_action)

    logger.info(message)

    # Update website in S3
    website.update(account_balance, cf_hourly_cost, margin, cf_action, cf_running)

