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

        self.bitcoin_addr = os.environ['BLOCKIO_BITCOIN_ADDR']

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

    def get_donate_button(self):
        """Get the account donate button.

            :returns (string, string, string) Account Donate Button HTML, Scripts and CSS
        """

        html = """
            <div style="font-size:16px;margin:0 auto;width:300px" class="blockchain-btn" "
                 data-address="{}"
                 data-shared="false">

              <div class="blockchain stage-begin">
                <img src="https://blockchain.info/Resources/buttons/donate_64.png"/>
              </div>
              <div class="blockchain stage-loading" style="text-align:center">
                <img src="https://blockchain.info/Resources/loading-large.gif"/>
              </div>
              <div class="blockchain stage-ready">
                 <p align="center">Please Donate To Bitcoin Address: <b>[[address]]</b></p>
                 <p align="center" class="qr-code"></p>
              </div>
              <div class="blockchain stage-paid">
                 Donation of <b>[[value]] BTC</b> Received. Thank You.
              </div>
              <div class="blockchain stage-error">
                <font color="red">[[error]]</font>
              </div>
            </div>
        """.format(self.bitcoin_addr)

        footer = """
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.0/jquery.min.js"></script>
            <script type="text/javascript" src="https://blockchain.info/Resources/js/pay-now-button.js"></script>
        """

        head = """

        """

        return html, footer, head