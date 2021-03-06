# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from cement.utils.misc import minimal_logger

from ..lib import aws
from ..objects.exceptions import ServiceError, AlreadyExistsError
from ..resources.strings import responses

LOG = minimal_logger(__name__)


def _make_api_call(operation_name, **operation_options):
    return aws.make_api_call('ec2', operation_name, **operation_options)


def get_key_pairs(region=None):
    result = _make_api_call('describe-key-pairs', region=region)
    return result['KeyPairs']


def import_key_pair(keyname, key_material, region=None):
    try:
        result = _make_api_call('import-key-pair', key_name=keyname,
                    public_key_material=key_material,
                    region=region)
    except ServiceError as e:
        if e.message.endswith('already exists.'):
            raise AlreadyExistsError(e.message)
        else:
            raise

    return result


def describe_instance(instance_id, region=None):
    result = _make_api_call('describe-instances',
                            instance_ids=[instance_id],
                            region=region)
    return result['Reservations'][0]['Instances'][0]


def revoke_ssh(security_group_id, region=None):
    try:
        _make_api_call('revoke-security-group-ingress',
                   group_id=security_group_id, ip_protocol='tcp',
                   to_port=22, from_port=22, cidr_ip='0.0.0.0/0',
                   region=region)
    except ServiceError as e:
        if e.message.startswith(responses['ec2.sshalreadyopen']):
            #ignore
            pass
        else:
            raise


def authorize_ssh(security_group_id, region=None):
    try:
        _make_api_call('authorize-security-group-ingress',
                   group_id=security_group_id, ip_protocol='tcp',
                   to_port=22, from_port=22, cidr_ip='0.0.0.0/0',
                   region=region)
    except ServiceError as e:
        if e.code == 'InvalidPermission.Duplicate':
            #ignore
            pass
        else:
            raise