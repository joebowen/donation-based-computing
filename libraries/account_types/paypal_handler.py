try:
    import unzip_requirements
except ImportError:
    pass

import base64
import os
import boto3
from paypal import PayPalInterface, PayPalConfig

kms = boto3.client('kms')


class Paypal:
    """Class to handle the Paypal donation accounts."""

    def __init__(self):
        account_settings = dict()

        account_settings['username'] = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['PAYPAL_USERNAME']))[u'Plaintext'].decode()

        account_settings['password'] = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['PAYPAL_PASSWORD']))[u'Plaintext'].decode()

        account_settings['api_signature'] = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['PAYPAL_API_SIGNATURE']))[u'Plaintext'].decode()

        config = PayPalConfig(API_USERNAME=account_settings['username'],
                              API_PASSWORD=account_settings['password'],
                              API_SIGNATURE=account_settings['api_signature'],
                              DEBUG_LEVEL=0)

        self.paypal = PayPalInterface(config=config)

    def get_balance(self):
        """Get the account balance.

            :returns float Account Balance
        """

        balance = self.paypal._call('GetBalance')

        return float("{0:.2f}".format(balance))