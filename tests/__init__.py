from unittest import TestCase
from mock import patch
from nose.tools import assert_is_instance, assert_list_equal, eq_

from flask import Flask
from flask import _app_ctx_stack as stack
from flask_boto3 import Boto3


@patch('boto3.resource')
class TestFlaskBoto3(TestCase):

    def setUp(self):
        self.app = Flask('unit_tests')
        self.app.config['BOTO3_REGION'] = 'eu-west-1'

    def test_001_populate_application_context(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['s3', 'sqs']
        b = Boto3(self.app)
        with self.app.app_context():
            assert_is_instance(b.connections, dict)
            eq_(len(b.connections), 2)
            assert_is_instance(stack.top.boto3_cns, dict)
            eq_(len(stack.top.boto3_cns), 2)

    def test_002_instantiate_connectors(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['s3', 'sqs', 'dynamodb']
        b = Boto3(self.app)
        with self.app.app_context():
            b.connections
            eq_(mock_resource.call_count, 3)
            assert_list_equal(
                sorted([i[0][0] for i in mock_resource.call_args_list]),
                sorted(self.app.config['BOTO3_SERVICES'])
            )

    def test_003_pass_credentials_through_app_conf(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['s3']
        self.app.config['BOTO3_ACCESS_KEY'] = 'access'
        self.app.config['BOTO3_SECRET_KEY'] = 'secret'
        b = Boto3(self.app)
        with self.app.app_context():
            b.connections
            mock_resource.assert_called_once_with(
                's3',
                'eu-west-1',
                aws_access_key_id='access',
                aws_secret_access_key='secret'
            )

    def test_004_pass_optional_params_through_conf(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['dynamodb']
        self.app.config['BOTO3_ACCESS_KEY'] = 'access'
        self.app.config['BOTO3_SECRET_KEY'] = 'secret'
        self.app.config['BOTO3_OPTIONAL_PARAMS'] = {
            'dynamodb': {
                'args': ('eu-west-1'),
                'kwargs': {
                    'fake_param': 'fake_value'
                }
            }
        }
        b = Boto3(self.app)
        with self.app.app_context():
            b.connections
            mock_resource.assert_called_once_with(
                'dynamodb',
                'eu-west-1',
                aws_access_key_id='access',
                aws_secret_access_key='secret',
                fake_param='fake_value'
            )

    def test_005_check_boto_clients_are_available(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['s3', 'sqs']
        b = Boto3(self.app)
        with self.app.app_context():
            clients = b.clients
            eq_(len(clients), len(self.app.config['BOTO3_SERVICES']))
            print(clients)

    def test_006_check_boto_resources_are_available(self, mock_resource):
        self.app.config['BOTO3_SERVICES'] = ['s3', 'sqs']
        b = Boto3(self.app)
        with self.app.app_context():
            resources = b.resources
            eq_(len(resources), len(self.app.config['BOTO3_SERVICES']))
            print(resources)
