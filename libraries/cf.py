try:
    import unzip_requirements
except ImportError:
    pass

import boto3
import dryscrape
import re
import logging

from bs4 import BeautifulSoup
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cf_client = boto3.client('cloudformation')


class CF:
    """Class to handle the CloudFormation."""
    def __init__(self, stack_name, margin=5):
        self.stack_name = stack_name
        self.margin = margin
        self.is_running = False

        with open('/var/task/templates/cf_template.yml', 'r') as template_file:
            self.cf_template = template_file.read()

        self.get_cost()

    def get_cost(self):
        """Get the cost per hour of the CloudFormation template.

            :returns float cost_per_hour
        """

        # TODO: Fix this and make it actually estimate the hourly costs.
        #  cost_url = cf_client.estimate_template_cost(TemplateBody=self.cf_template)
        #
        # session = dryscrape.Session()
        # session.visit(cost_url['Url'])
        # response = session.body()
        # soup = BeautifulSoup(response)
        # monthly_bill = soup.find(text=re.compile("Estimate of your Monthly Bill \(\$ (.*)\)"))
        #
        # monthly_cost = float(re.match("Estimate of your Monthly Bill \(\$ (.*)\)", monthly_bill).groups()[0])
        #
        # self.cost_per_hour = monthly_cost / 730

        self.cost_per_hour = .02

        return self.cost_per_hour

    def make_decision(self, account_balance):
        """Make the decision given the cost of the CloudFormation template and
            the current account balance.

            :float account_balance The current account balance

            :returns string Decision
        """

        if self.cost_per_hour * float(self.margin) < account_balance:
            if self.running():
                cf_action = 'stay'
            else:
                cf_action = 'create'
                self.create()
        else:
            if self.running():
                cf_action = 'delete'
                self.delete()
            else:
                cf_action = 'stay'

        return cf_action

    def running(self):
        """Check to see if the CloudFormation template is running or not.

            :returns boolean True if running, False otherwise.
        """
        self.is_running = True

        try:
            cf_client.describe_stacks(StackName=self.stack_name)
        except ClientError as e:
            logger.info(e)
            self.is_running = False

        return self.is_running

    def create(self):
        """Create the CloudFormation template."""
        cf_client.create_stack(StackName=self.stack_name,
                               TemplateBody=self.cf_template)

    def update(self, params):
        """Update the CloudFormation template.

            :dict params The parameter list of dictionaries to update the CloudFormation stack.
        """
        cf_client.update_stack(StackName=self.stack_name,
                               Parameters=params)

    def delete(self):
        """Delete the CloudFormation template."""
        cf_client.delete_stack(StackName=self.stack_name)
