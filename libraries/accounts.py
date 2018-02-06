try:
    import unzip_requirements
except ImportError:
    pass

import os

from .account_types.paypal_handler import Paypal
from .account_types.blockio_bitcoin_handler import Bitcoin


class Accounts:
    """Class to handle the donation accounts."""

    def __init__(self):
        if os.environ['ACCOUNT_TYPE'] == 'paypal':
            self.account = Paypal()
        elif os.environ['ACCOUNT_TYPE'] == 'blockio_bitcoin':
            self.account = Bitcoin()

    def get_balance(self):
        """Get the account balance.

            :returns float Account Balance
        """

        return self.account.get_balance()
