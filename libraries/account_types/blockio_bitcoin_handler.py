try:
    import unzip_requirements
except ImportError:
    pass

import base64
import os
import boto3
from block_io import BlockIo

kms = boto3.client('kms')


class Bitcoin:
    """Class to handle the Bitcoin donation accounts using Block.io"""

    def __init__(self):
        account_settings = dict()

        account_settings['bitcoin_api_key'] = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['BLOCKIO_BITCOIN_API_KEY']))[u'Plaintext'].decode()

        account_settings['secret_pin'] = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['BLOCKIO_SECRET_PIN']))[u'Plaintext'].decode()

        self.bitcoin_addr = kms.decrypt(
            CiphertextBlob=base64.b64decode(os.environ['BLOCKIO_BITCOIN_ADDR']))[u'Plaintext'].decode()

        self.block_io = BlockIo(account_settings['bitcoin_api_key'], account_settings['secret_pin'], 2)

    def get_balance(self):
        """Get the account balance using Block.io and checking the CoinBase exchange rate.

            :returns float Account Balance
        """

        btc_balance = self.block_io.get_address_balance(addresses=self.bitcoin_addr)

        btc_balance = float(btc_balance['data']['available_balance'])

        current_price = self.block_io.get_current_price(price_base='USD')

        current_price = float(
            next((x for x in current_price['data']['prices'] if x['exchange'] == 'coinbase'), None)['price'])

        balance = current_price * btc_balance

        return float("{0:.2f}".format(balance))