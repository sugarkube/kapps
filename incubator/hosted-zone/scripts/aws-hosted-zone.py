#!/usr/bin/env python3
#
# This either:
# * Creates a placeholder VPC and private hosted zone or
# * Associates a VPC with the hosted zone and deletes the placeholder
#

import argparse
import subprocess
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

AWS="aws"       # path to the AWS CLI binary


def main():
    parser = argparse.ArgumentParser(description='Creates/updates hosted zones for kops.')
    parser.add_argument(dest='hosted_zone_name', help='Hosted zone to create/update')
    parser.add_argument(dest='vpc_name', help='Name of the VPC to associate')

    args = parser.parse_args()
    return run(args.hosted_zone_name, args.vpc_name)


def run(hosted_zone_name, vpc_name):
    if not hosted_zone_name.endswith('.'):
        hosted_zone_name += '.'

    hosted_zone_id = _get_hosted_zone_id(hosted_zone_name)
    logging.info("Hosted zone ID is: '%s'" % hosted_zone_id)

    if not hosted_zone_id:
        logging.info("Hosted zone doesn't exist... Will create it.")
        hosted_zone_id = _create_hosted_zone(hosted_zone_name)


def _get_vpc_by_name(vpc_name):
    """
    Returns the ID of a VPC by name
    :param vpc_name:
    :return: VPC ID
    """
    logging.info("Searching for VPC '%s'" % vpc_name)
    result = subprocess.run(args=[AWS, '--output', 'text', 'ec2', 'describe-vpcs',
                                  '--filters', 'Name=tag:Name,VAlues=%s' % vpc_name,
                                  '--query', 'Vpcs[*].VpcId | [0]'],
                            capture_output=True)
    logging.debug('result=%s' % result)
    result = result.stdout.decode("utf-8").strip()
    if result == 'None':
        result = None

    logging.debug("Returning result '%s'" % result)

    return result


def _create_hosted_zone(hosted_zone_name):
    """
    Creates a hosted zone and returns its ID
    :param hosted_zone_name:
    :return: The hosted zone ID
    """


def _get_hosted_zone_id(hosted_zone_name):
    """
    Returns the ID of a hosted zone if it exists
    :param hosted_zone_name:
    :return:
    """
    logging.info("Searching for hosted zone '%s'" % hosted_zone_name)
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'list-hosted-zones', '--query',
                             'HostedZones[?Name == `%s` && Config.PrivateZone == `true`].Id | [0]' % hosted_zone_name],
                            capture_output=True)
    logging.debug('result=%s' % result)
    result = result.stdout.decode("utf-8").strip()
    if result == 'None':
        result = None

    logging.debug("Returning result '%s'" % result)

    return result


if __name__ == "__main__":
    sys.exit(main())
