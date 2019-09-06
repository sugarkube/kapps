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
import json
import tempfile
import os

logging.basicConfig(level=logging.DEBUG)

AWS=os.getenv("AWS", "aws")       # path to the AWS CLI binary


def main():
    parser = argparse.ArgumentParser(description='Creates/updates hosted zones for kops.')
    parser.add_argument(dest='hosted_zone_name', help='Hosted zone to update TTLs in (a domain name)')
    parser.add_argument(dest='name_servers', help='List of comma separated nameservers to update TTLs for')
    parser.add_argument('--ttl', help='Value of the TTL to set', default=60)

    args = parser.parse_args()
    return install(hosted_zone_name=args.hosted_zone_name, name_servers=args.name_servers.split(','), ttl=args.ttl)


def install(hosted_zone_name, name_servers, ttl):
    """
    Updates TTLs associated with a hosted zone for NS and SOA records
    :param hosted_zone_name:
    :param name_servers:
    """
    if not hosted_zone_name.endswith('.'):
        hosted_zone_name += '.'

    hosted_zone_id = _get_hosted_zone_id(hosted_zone_name)

    _update_ns_ttl(hosted_zone_name=hosted_zone_name,
                   hosted_zone_id=hosted_zone_id,
                   name_servers=name_servers,
                   ttl=ttl)
    _update_soa_ttl(hosted_zone_name=hosted_zone_name,
                   hosted_zone_id=hosted_zone_id,
                   name_servers=name_servers,
                   ttl=ttl)


def _get_hosted_zone_id(hosted_zone_name):
    """
    Returns the ID of a named hosted zone 
    :param hosted_zone_name: 
    :return: hosted zone ID
    """
    result = subprocess.run(args=[AWS, '--output', 'text', 'route53', 'list-hosted-zones',
                                  '--query', 'HostedZones[?Name == `%s`].Id | [0]' % hosted_zone_name],
                            capture_output=True)
    if not result.returncode == 0:
        raise RuntimeError("Failed to get the ID of hosted zone '%s': %s" % (hosted_zone_name, result))
    return result


def _update_ns_ttl(hosted_zone_name, hosted_zone_id, name_servers, ttl):
    """
    Writes JSON to update NS records
    :param hosted_zone_name:
    :param name_servers:
    :return:
    """
    records = []
    for server in name_servers:
        records.append({"Value": server})

    spec = {
        "Comment": "Update NS TTLs",
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "ResourceRecords": records,
                "Type": "NS",
                "Name": hosted_zone_name,
                "TTL": ttl,
            }
        }]
    }

    update_records(hosted_zone_id, spec)


def _update_soa_ttl(hosted_zone_name, hosted_zone_id, name_servers, ttl):
    """
    Writes JSON to update SOA records
    :param hosted_zone_name:
    :param name_servers:
    :return:
    """
    record_value = "%s. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400" % name_servers[0]

    spec = {
        "Comment": "Update SOA TTLs",
        "Changes": [{
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "ResourceRecords": [{
                    "Value": record_value
                }],
                "Type": "SOA",
                "Name": hosted_zone_name,
                "TTL": ttl,
            }
        }]
    }

    update_records(hosted_zone_id, spec)


def update_records(hosted_zone_id, spec):
    """
    Updates route53 record sets
    :param hosted_zone_id:
    :param spec: Dict of data to pass to the command
    """
    _, temp_path = tempfile.mkstemp(suffix=".json")
    with open(temp_path, 'w') as f:
        json.dump(spec, f)

    logging.info("Dumped json to file: %s" % temp_path)

    return subprocess.run(args=[AWS, 'route53', 'change-resource-record-sets',
                                '--hosted-zone-id', hosted_zone_id,
                                '--change-batch', 'file://%s' % temp_path])


if __name__ == "__main__":
    sys.exit(main())
