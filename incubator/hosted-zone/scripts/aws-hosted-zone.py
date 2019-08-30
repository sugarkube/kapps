#!/usr/bin/env python3
#
# This either:
# * Creates a placeholder VPC and private hosted zone or
# * Associates a VPC with the hosted zone and deletes the placeholder
#
# Note: This assumes that a VPC may exist with the same name as the hosted zone
#

import argparse
import subprocess
import sys
import logging
import time

logging.basicConfig(level=logging.DEBUG)

INSTALL="install"
DELETE="delete"
AWS="aws"       # path to the AWS CLI binary


def main():
    parser = argparse.ArgumentParser(description='Creates/updates hosted zones for kops.')
    parser.add_argument(dest='mode', choices=[INSTALL, DELETE], help='Mode to run in')
    parser.add_argument(dest='hosted_zone_name', help='Hosted zone to create/update (a domain name)')
    parser.add_argument('--vpc-region', help='Region to create the VPC in (when running in install mode)')

    args = parser.parse_args()
    return run(mode=args.mode, hosted_zone_name=args.hosted_zone_name, vpc_region=args.vpc_region)


def run(mode, hosted_zone_name, vpc_region):
    if mode == INSTALL:
        return install(hosted_zone_name=hosted_zone_name, vpc_region=vpc_region)
    elif mode == DELETE:
        return delete(hosted_zone_name=hosted_zone_name)


def delete(hosted_zone_name):
    """
    Deletes a hosted zone (used when deleting the kapp)
    :param hosted_zone_name:
    """
    if not hosted_zone_name.endswith('.'):
        hosted_zone_name += '.'

    hosted_zone_id = _get_hosted_zone_id(hosted_zone_name)
    logging.info("Hosted zone ID is: '%s'" % hosted_zone_id)

    if hosted_zone_id:
        _delete_hosted_zone(hosted_zone_id)

    placeholder_vpc_name = "placeholder %s" % hosted_zone_name
    vpc_id = _get_vpc_by_name(placeholder_vpc_name)
    if vpc_id:
        _delete_vpc(vpc_id)


def install(hosted_zone_name, vpc_region):
    """
    Creates/updates a hosted zone and its associated VPC and creates/deletes a placeholder VPC accordingly
    :param hosted_zone_name:
    :param vpc_region:
    """
    if not hosted_zone_name.endswith('.'):
        hosted_zone_name += '.'

    hosted_zone_id = _get_hosted_zone_id(hosted_zone_name)
    logging.info("Hosted zone ID is: '%s'" % hosted_zone_id)

    placeholder_vpc_name = "placeholder %s" % hosted_zone_name

    if not hosted_zone_id:
        logging.info("Hosted zone doesn't exist... Will create it.")
        hosted_zone_id = _create_hosted_zone(hosted_zone_name=hosted_zone_name,
                                             placeholder_vpc_name=placeholder_vpc_name,
                                             vpc_region=vpc_region)
    
    # see if the main (non-placeholder) vpc exists
    vpc_name = hosted_zone_name.rstrip('.')
    vpc_id = _get_vpc_by_name(vpc_name)
    
    if not vpc_id:
        logging.info("No main VPC exists called '%s'. Nothing else to do." % vpc_name)
        return
    
    # if it does exist, we need to associate it with the hosted zone if it's not already,
    # and delete the placeholder if it exists
    if _is_vpc_associated_with_hosted_zone(vpc_id=vpc_id, hosted_zone_id=hosted_zone_id):
        logging.info("Hosted zone '%s' is already associated with VPC '%s' (ID='%s')" % 
                     (hosted_zone_id, vpc_name, vpc_id))
    else:
        # associate the vpc with the hosted zone
        _associate_vpc_with_hosted_zone(vpc_id=vpc_id, 
                                        hosted_zone_id=hosted_zone_id, 
                                        vpc_region=vpc_region)
    
    placeholder_vpc_id = _get_vpc_by_name(placeholder_vpc_name)
    if placeholder_vpc_id:
        # delete the placeholder VPC
        if _is_vpc_associated_with_hosted_zone(placeholder_vpc_id, hosted_zone_id):
            _dissociate_vpc_from_hosted_zone(vpc_id=vpc_id,
                                             hosted_zone_id=hosted_zone_id,
                                             vpc_region=vpc_region)
        
        logging.info("Deleting placeholder VPC '%s'" % placeholder_vpc_id)
        _delete_vpc(placeholder_vpc_id)
    else:
        logging.info("Couldn't find a placeholder VPC called '%s'. Assume it's already been deleted." % placeholder_vpc_name)
        

def _dissociate_vpc_from_hosted_zone(vpc_id, hosted_zone_id, vpc_region):
    """
    Dissociates a VPC from a hosted zone
    :param vpc_id: 
    :param hosted_zone_id: 
    :param vpc_region: 
    """
    logging.info("Dissociating VPC '%s' with hosted zone '%s'" % (vpc_id, hosted_zone_id))
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'dissociate-vpc-from-hosted-zone',
                                  '--hosted-zone-id', hosted_zone_id, 
                                  '--vpc', 'VPCRegion=%s,VPCId=%s' % (vpc_region, vpc_id)],
                            capture_output=True)
    logging.debug('result=%s' % result)

    if not result.returncode == 0:
        raise RuntimeError("Failed to dissociate VPC '%s' from hosted zone '%s': %s" % (
            vpc_id, hosted_zone_id, result))
        

def _associate_vpc_with_hosted_zone(vpc_id, hosted_zone_id, vpc_region):
    """
    Associate a VPC with a hosted zone
    :param vpc_id: 
    :param hosted_zone_id: 
    :param vpc_region: 
    """
    logging.info("Associating VPC '%s' with hosted zone '%s'" % (vpc_id, hosted_zone_id))
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'associate-vpc-with-hosted-zone',
                                  '--hosted-zone-id', hosted_zone_id, 
                                  '--vpc', 'VPCRegion=%s,VPCId=%s' % (vpc_region, vpc_id)],
                            capture_output=True)
    logging.debug('result=%s' % result)

    if not result.returncode == 0:
        raise RuntimeError("Failed to associate VPC '%s' with hosted zone '%s': %s" % (
            vpc_id, hosted_zone_id, result))


def _is_vpc_associated_with_hosted_zone(vpc_id, hosted_zone_id):
    """
    Checks whether a VPC is associated with a hosted zone
    :param vpc_id: 
    :param hosted_zone_id: 
    :return: boolean
    """
    logging.info("Checking whether VPC '%s' is associated with hosted zone '%s'" % (vpc_id, hosted_zone_id))
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'get-hosted-zone',
                                  '--id', hosted_zone_id, 
                                  '--query', 'VPCs[?VPCId == `%s`].VPCId | [0]' % vpc_id],
                            capture_output=True)

    if not result.returncode == 0:
        raise RuntimeError("Failed to check whether VPC '%s' is associated with hosted zone '%s': %s" % (
            vpc_id, hosted_zone_id, result))
    
    logging.debug('result=%s' % result)
    result = result.stdout.decode("utf-8").strip()
    return result == vpc_id


def _get_vpc_by_name(vpc_name):
    """
    Returns the ID of a VPC by name
    :param vpc_name:
    :return: VPC ID
    """
    logging.info("Searching for VPC '%s'" % vpc_name)
    result = subprocess.run(args=[AWS, '--output', 'text', 'ec2', 'describe-vpcs',
                                  '--filters', 'Name=tag:Name,Values=%s' % vpc_name,
                                  '--query', 'Vpcs[*].VpcId | [0]'],
                            capture_output=True)
    logging.debug('result=%s' % result)

    if not result.returncode == 0:
        raise RuntimeError("Failed to create VPC '%s': %s" % (vpc_name, result))

    result = result.stdout.decode("utf-8").strip()
    if result == 'None':
        result = None

    logging.debug("Returning result '%s'" % result)

    return result


def _delete_vpc(vpc_id):
    """
    Deletes a VPC by name
    :param vpc_id: 
    """
    logging.info("Deleting VPC '%s'" % vpc_id)
    result = subprocess.run(args=[AWS, '--output', 'text', 'ec2', 'delete-vpc',
                                  '--vpc-id', vpc_id],
                            capture_output=True)
    if not result.returncode == 0:
        raise RuntimeError("Failed to delete VPC '%s': %s" % (vpc_id, result))


def _create_vpc(vpc_name):
    """
    Creates a VPC and tags it with the given name
    :param vpc_name:
    :return:
    """
    logging.info("Creating a VPC called '%s'" % vpc_name)
    result = subprocess.run(args=[AWS, '--output', 'text', 'ec2', 'create-vpc',
                                  '--cidr-block', '10.0.0.0/28',        # this is a temporary placeholder so we can use anything
                                  '--query', 'Vpc.VpcId'],
                            capture_output=True)
    if not result.returncode == 0:
        raise RuntimeError("Failed to create VPC '%s': %s" % (vpc_name, result))

    logging.debug('result=%s' % result)

    vpc_id = result.stdout.decode("utf-8").strip()
    if vpc_id == 'None':
        vpc_id = None

    logging.info("Tagging VPC '%s'" % vpc_name)
    result = subprocess.run(args=[AWS, '--output', 'text', 'ec2', 'create-tags', '--resources', vpc_id,
                                  '--tags', 'Key=Name,Value=%s' % vpc_name],
                            capture_output=False)

    if not result.returncode == 0:
        raise RuntimeError("Failed to tag VPC '%s': %s" % (vpc_name, result))

    logging.info("VPC '%s' (ID=%s) created and tagged" % (vpc_name, vpc_id))

    return vpc_id


def _delete_hosted_zone(hosted_zone_id):
    """
    Delete a hosted zone
    :param hosted_zone_id:
    """
    logging.info("Deleting hosted zone '%s'" % hosted_zone_id)
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'delete-hosted-zone',
                                  '--id', hosted_zone_id],
                            capture_output=True)

    if not result.returncode == 0:
        raise RuntimeError("Failed to delete hosted zone '%s': %s" % (hosted_zone_id, result))


def _create_hosted_zone(hosted_zone_name, placeholder_vpc_name, vpc_region):
    """
    Creates a hosted zone and returns its ID
    :param hosted_zone_name:
    :param placeholder_vpc_name: Name of the placeholder VPC to create if it doesn't already exist
    :param vpc_name: Region to create the VPC in
    :return: The hosted zone ID
    """
    placeholder_vpc_id = _get_vpc_by_name(placeholder_vpc_name)
    if not placeholder_vpc_id:
        placeholder_vpc_id = _create_vpc(placeholder_vpc_name)

    logging.info("Creating private hosted zone '%s' for placeholder VPC %s in region %s" % (
        hosted_zone_name, placeholder_vpc_id, vpc_region))
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'create-hosted-zone',
                                  '--caller-reference', str(time.time()),
                                  '--vpc', "VPCRegion=%s,VPCId=%s" % (vpc_region, placeholder_vpc_id),
                                  '--name', hosted_zone_name, '--hosted-zone-config', 'PrivateZone=true',
                                  '--query', 'HostedZone.Id'],
                            capture_output=True)

    if not result.returncode == 0:
        raise RuntimeError("Failed to create hosted zone '%s': %s" % (hosted_zone_name, result))

    logging.debug('result=%s' % result)
    hosted_zone_id = result.stdout.decode("utf-8").strip()
    if hosted_zone_id == 'None':
        hosted_zone_id = None

    return hosted_zone_id


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

    if not result.returncode == 0:
        raise RuntimeError("Failed to create VPC '%s': %s" % (hosted_zone_name, result))

    logging.debug('result=%s' % result)
    result = result.stdout.decode("utf-8").strip()
    if result == 'None':
        result = None

    logging.debug("Returning result '%s'" % result)

    return result


if __name__ == "__main__":
    sys.exit(main())
