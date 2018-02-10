try:
    import unzip_requirements
except ImportError:
    pass

import os
import jinja2
import boto3

from .account_types.paypal_handler import Paypal
from .account_types.blockio_bitcoin_handler import Bitcoin

s3 = boto3.client('s3')


class Website:
    """Class to handle the donation website."""

    def __init__(self):
        if os.environ['ACCOUNT_TYPE'] == 'paypal':
            self.account = Paypal()
        elif os.environ['ACCOUNT_TYPE'] == 'blockio_bitcoin':
            self.account = Bitcoin()

    def render(self, tpl_path, context):
        """Render a Jinja2 template.

            :string tpl_path The Jinja2 template path

            :return: The Jinja2 rendered template
        """

        path, filename = os.path.split(tpl_path)

        rendered = jinja2.Environment(
                loader=jinja2.FileSystemLoader(path or './')
            ).get_template(filename).render(context)

        return rendered

    def update(self, account_balance, hourly_cost, margin, action, is_running):
        """Update the donation website.

            :float account_balance The current account balance
            :float hourly_cost The hourly cost of the CloudFormation template
            :int margin The number of hours worth of account balance required to run the CloudFormation template
            :string action The desired action to take (create/delete/stay)
        """

        donate_html, donate_footer, donate_head = self.account.get_donate_button()

        context = {
            'account_balance': account_balance,
            'hourly_cost': hourly_cost,
            'margin': margin,
            'action': action,
            'project_name': os.environ['PROJECT_NAME'],
            'project_url': os.environ['PROJECT_URL'],
            'is_running': str(is_running),
            'donate_html': donate_html,
            'donate_head': donate_head,
            'donate_footer': donate_footer,
        }

        result = self.render('/var/task/templates/index.html', context)

        s3.put_object(Body=result, Bucket=os.environ['WEBSITE_BUCKET'], Key='index.html', ContentType='text/html')

