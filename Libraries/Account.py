from paypal import PayPalInterface, PayPalConfig


class Account:
    """Class to handle the donation accounts."""
    def __init__(self, username, password, api_signature, account_type):
        self.username = username
        self.password = password
        self.api_signature = api_signature
        self.account_type = account_type

    def get_balance(self):
        """Get the account balance.

            :returns float Account Balance
        """

        if self.account_type == 'paypal':
            config = PayPalConfig(API_USERNAME=self.username,
                                  API_PASSWORD=self.password,
                                  API_SIGNATURE=self.api_signature,
                                  DEBUG_LEVEL=0)

            paypal = PayPalInterface(config=config)

            balance = paypal._call('GetBalance')
        else:
            raise Exception("Unable to get balance.")

        return balance
