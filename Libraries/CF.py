import boto3
import urllib2

client = boto3.client('cloudformation')


class CF:
    """Class to handle the CloudFormation."""
    def __init__(self, stack_name, margin=5):
        self.stack_name = stack_name
        self.margin = margin
        self.is_running = False

        with open('cf_template.yml', 'r') as template_file:
            self.cf_template = template_file.read().replace('\n', '')

        self.get_cost()

    def get_cost(self):
        """Get the cost per hour of the CloudFormation template.

            :returns float cost_per_hour
        """

        cost_url = client.estimate_template_cost(TemplateBody=self.cf_template)

        self.cost_per_hour = urllib2.urlopen(cost_url).read()

        return self.cost_per_hour

    def make_decision(self, account_balance):
        """Make the decision given the cost of the CloudFormation template and
            the current account balance.

            :float account_balance The current account balance

            :returns string Decision
        """

        if self.cost_per_hour > account_balance * self.margin:
            if self.running():
                cf_action = 'stay'
            else:
                cf_action = 'create'
                self.create()
        else:
            cf_action = 'delete'
            self.delete()

        return cf_action

    def running(self):
        """Check to see if the CloudFormation template is running or not.

            :returns boolean True if running, False otherwise.
        """
        self.is_running = True

        try:
            client.describe_stacks(StackName=self.stack_name)
        except boto3.AmazonCloudFormationException:
            self.is_running = False

        return self.is_running

    def launch(self):
        """Launch the CloudFormation template."""
        client.create_stack(StackName=self.stack_name,
                            TemplateBody=self.cf_template)

    def update(self, params):
        """Update the CloudFormation template.

            :dict params The parameter list of dictionaries to update the CloudFormation stack.
        """
        client.update_stack(StackName=self.stack_name,
                            Parameters=params)

    def delete(self):
        """Delete the CloudFormation template."""
        client.delete_stack(StackName=self.stack_name)
