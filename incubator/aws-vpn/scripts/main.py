#!/usr/bin/env python3
#
# This script creates a VPN Endpoint (generating all required certificates) and downloads an OpenVPN config file to
# access the endpoint.
#
# For the process, see https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
#
# Future enhancements: Wait for all resources to become ready before returning (but disable with a flag)
#

import argparse
import subprocess
import sys
import logging
import os
import json
import time
import uuid

logging.basicConfig(level=logging.DEBUG)

AWS=os.getenv("AWS", "aws")       # path to the AWS CLI binary
CFSSL=os.getenv("CFSSL", "cfssl")       # path to the cfssl binary
CFSSL_JSON=os.getenv("CFSSL_JSON", "cfssljson")       # path to the cfssljson binary

INSTALL="install"
DELETE="delete"

CLIENT="client"
SERVER="server"

def main():
    parser = argparse.ArgumentParser(description='Creates/updates hosted zones for kops.')
    parser.add_argument(dest='mode', choices=[INSTALL, DELETE], help='Mode to run in')
    parser.add_argument(dest='cluster_name', help='Name of the cluster')
    parser.add_argument(dest='vpc_name', help='Name of the VPC to create an endpoint for')
    parser.add_argument(dest='hostnames', help='Common names to set in the client & server certificates (comma-separated)')
    parser.add_argument('--out-dir', help='Path to the directory to write files to', default='../cfssl/_generated_certs')
    parser.add_argument('--ovpn-out-dir', help='Directory to write the OVPN file to', default='~/Downloads')
    parser.add_argument('--cert-json', help='Path to a cfssl JSON file', default='../cfssl/cert.json')

    args = parser.parse_args()

    cluster_name = args.cluster_name

    try:
        if args.mode == INSTALL:
            install(args=args, cluster_name=cluster_name)
        else:
            delete(args=args,
                   cluster_name=cluster_name,
                   vpc_name=args.vpc_name)
    except Exception as e:
        logging.exception("An error occurred: %s", e)
        return 1


def delete(args, cluster_name, vpc_name):
    """
    Delete a VPN endpoint. If it doesn't exist, do nothing.
    :param args:
    """
    vpc_id = _get_vpc_by_name(vpc_name)
    if not vpc_id:
        print("VPC '%s' not found. Nothing to do." % vpc_name)
        # don't raise an exception, just return
        return

    vpn_endpoint_id = _get_vpn_endpoint(cluster_name=cluster_name)

    if vpn_endpoint_id:
        pass
        # delete the 0/0 entry from the routing table
        _delete_vpn_route(vpn_endpoint_id=vpn_endpoint_id, cidr='0.0.0.0/0')

        # revoke the authorisation
        _revoke_ingress_authorisation(vpn_endpoint_id=vpn_endpoint_id, cidr="0.0.0.0/0")

        # dissocate the endpoint from subnets
        _dissociate_endpoint_from_subnets(vpn_endpoint_id=vpn_endpoint_id)

        # delete the VPN
        _delete_vpn_endpoint(vpn_endpoint_id=vpn_endpoint_id)

    # delete the certs
    cert_arns = _get_certs(cluster_name=cluster_name)
    for cert_arn in cert_arns.values():
        _delete_cert(cert_arn)

    print("VPN for '%s' deleted" % cluster_name)


def _delete_vpn_endpoint(vpn_endpoint_id):
    """
    Delete's a VPN endpoint
    :param vpn_endpoint_id:
    """
    command = '%s ec2 delete-client-vpn-endpoint --client-vpn-endpoint-id=%s' % (AWS, vpn_endpoint_id)
    logging.info("Executing command: %s" % command)
    subprocess.run(command, shell=True)


def _dissociate_endpoint_from_subnets(vpn_endpoint_id):
    """
    Deletes all subnet associations with the endpoint
    :param vpn_endpoint_id:
    """
    associations = _get_subnet_associations(vpn_endpoint_id)

    for association in associations:
        command = '%s ec2 disassociate-client-vpn-target-network --client-vpn-endpoint-id=%s ' \
                  '--association-id=%s' % (AWS, vpn_endpoint_id, association["AssociationId"])
        logging.info("Executing command: %s" % command)
        subprocess.run(command, shell=True)


def _get_ingress_authorisations(vpn_endpoint_id):
    """
    Returns a list of VPN ingress authorisation rules
    :param vpn_endpoint_id:
    :return: list
    """
    command = '%s ec2 describe-client-vpn-authorization-rules --client-vpn-endpoint-id=%s' % (AWS, vpn_endpoint_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())
    return response['AuthorizationRules']


def _revoke_ingress_authorisation(vpn_endpoint_id, cidr):
    """
    Revokes a VPN ingress authorisation
    :param vpn_endpoint_id:
    :param cidr:
    """
    authorisations = _get_ingress_authorisations(vpn_endpoint_id)

    for auth in authorisations:
        if auth['DestinationCidr'] == cidr:
            command = '%s ec2 revoke-client-vpn-ingress --client-vpn-endpoint-id=%s ' \
                      '--target-network-cidr=%s --revoke-all-groups' % (AWS, vpn_endpoint_id, cidr)
            logging.info("Executing command: %s" % command)
            subprocess.run(command, shell=True, check=True)


def _delete_cert(cert_arn):
    """
    Deletes a certificate from ACM
    :param cert_arn: ARN of the cert to delete
    """
    command = '%s acm delete-certificate --certificate-arn=%s' % (AWS, cert_arn)
    logging.info("Executing command: %s" % command)
    subprocess.run(command, shell=True, check=True)


def install(args, cluster_name):
    """
    Create a VPN endpoint if it doesn't exist (if it does, do nothing)
    :param args:
    :param cluster_name: Name of the cluster (used for namespacing resources)
    """
    out_dir = args.out_dir
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    vpc_name = args.vpc_name

    vpc_id = _get_vpc_by_name(vpc_name)
    if not vpc_id:
        # this is an error case
        raise RuntimeError("Error: VPC '%s' not found" % args.vpc_name)

    print("VPC '%s' has ID '%s'" % (vpc_name, vpc_id))

    cert_arns = _get_certs(cluster_name=cluster_name)

    if len(cert_arns) == 1:
        raise RuntimeError("Only a single imported cert could be found")
    elif len(cert_arns) == 2:
        print("Certs already exist")

        # make sure that we have the cert and private key on disk or we won't be able to modify the config file
        required_paths = [
            os.path.join(out_dir, "%s.pem" % CLIENT),
            os.path.join(out_dir, "%s-key.pem" % CLIENT),
        ]

        for path in required_paths:
            if not os.path.exists(path):
                raise RuntimeError("Certs have already been imported but the local files don't exist. "
                                   "We need: %s" % ', '.join(required_paths))

    else:
        print("No certs exist. Will create and import them...")

        _generate_certs(cluster_name=cluster_name,
                        cert_json=args.cert_json,
                        out_dir=out_dir,
                        hostnames=args.hostnames)

        cert_arns = _import_certs(out_dir=out_dir,
                                  cluster_name=cluster_name)

    # get details of the VPC's CIDR range and subnets
    vpc_details = _describe_vpc(vpc_id=vpc_id)

    vpn_endpoint_id = _get_vpn_endpoint(cluster_name=cluster_name)

    if not vpn_endpoint_id:
        vpn_endpoint_id = _create_vpn_endpoint(cert_arns=cert_arns,
                                               cluster_name=cluster_name,
                                               vpc_details=vpc_details)

    # associate the endpoint with the private subnets
    _associate_endpoint_with_subnets(vpn_endpoint_id=vpn_endpoint_id,
                                     vpc_details=vpc_details)

    # authorise ingress
    _authorise_ingress(vpn_endpoint_id=vpn_endpoint_id, cidr="0.0.0.0/0")

    # create a route for 0/0
    _create_vpn_route(vpn_endpoint_id=vpn_endpoint_id, cidr='0.0.0.0/0')

    cert_path = os.path.join(out_dir, "%s.pem" % CLIENT)
    key_path = os.path.join(out_dir, "%s-key.pem" % CLIENT)

    _export_config_file(endpoint_id=vpn_endpoint_id,
                        cluster_name=cluster_name,
                        cert_path=cert_path,
                        key_path=key_path,
                        output_dir=os.path.abspath(os.path.expanduser(args.ovpn_out_dir)))


def _delete_vpn_route(vpn_endpoint_id, cidr):
    """
    Delete's a VPN route
    :param vpn_endpoint_id:
    :param cidr:
    :return:
    """
    routes = _get_vpn_routes(vpn_endpoint_id=vpn_endpoint_id)

    for route in routes:
        if route['DestinationCidr'] == cidr:
            command = '%s ec2 delete-client-vpn-route --client-vpn-endpoint-id=%s ' \
                      '--target-vpc-subnet-id=%s --destination-cidr-block=%s' % (
                AWS, vpn_endpoint_id, route['TargetSubnet'], cidr)
            logging.info("Executing command: %s" % command)
            subprocess.run(command, shell=True, check=True)


def _get_vpn_routes(vpn_endpoint_id):
    """
    Returns a list of VPN routes associated with the VPN endpoint
    :param vpn_endpoint_id:
    :return: list
    """
    command = '%s ec2 describe-client-vpn-routes --client-vpn-endpoint-id=%s' % (AWS, vpn_endpoint_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())
    return response['Routes']


def _get_subnet_associations(vpn_endpoint_id):
    """
    Returns a list of subnets associated with the VPN
    :param vpn_endpoint_id:
    :return: list
    """
    command = '%s ec2 describe-client-vpn-target-networks --client-vpn-endpoint-id=%s' % (AWS, vpn_endpoint_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())

    return response['ClientVpnTargetNetworks']


def _create_vpn_route(vpn_endpoint_id, cidr):
    """
    Creates an entry in the VPN routing table if it doesn't exist
    :param vpn_endpoint_id: ID of the VPN to create the entry for
    :param cidr: CIDR block to create a route for
    """
    routes = _get_vpn_routes(vpn_endpoint_id=vpn_endpoint_id)

    for route in routes:
        if route['DestinationCidr'] == cidr:
            print("VPN '%s' already has a route for '%s'" % (vpn_endpoint_id, cidr))
            return

    associations = _get_subnet_associations(vpn_endpoint_id=vpn_endpoint_id)
    subnet_ids = [x['TargetNetworkId'] for x in associations]
    if len(subnet_ids) == 0:
        raise RuntimeError("No subnets associated with VPN '%s'" % vpn_endpoint_id)

    command = '%s ec2 create-client-vpn-route --client-vpn-endpoint-id=%s ' \
              '--destination-cidr-block=%s ' \
              '--target-vpc-subnet-id=%s ' \
              '--description=Internet' % (AWS, vpn_endpoint_id, cidr, subnet_ids[0])
    logging.info("Executing command: %s" % command)
    subprocess.run(command, shell=True, check=True)


def _authorise_ingress(vpn_endpoint_id, cidr):
    """
    Permits ingress into the VPN from all users
    :param cidr:
    :param vpn_endpoint_id:
    """
    authorisations = _get_ingress_authorisations(vpn_endpoint_id)

    for auth in authorisations:
        if auth['DestinationCidr'] == cidr:
            print("VPN '%s' has already authorised CIDR '%s'" % (vpn_endpoint_id, cidr))
            return

    print("Permitting ingress to VPN '%s'" % vpn_endpoint_id)
    command = '%s ec2 authorize-client-vpn-ingress --client-vpn-endpoint-id=%s ' \
              '--target-network-cidr=%s --authorize-all-groups ' \
              '--description "Permit all"' % (AWS, vpn_endpoint_id, cidr)
    logging.info("Executing command: %s" % command)
    subprocess.run(command, shell=True, check=True)


def _associate_endpoint_with_subnets(vpn_endpoint_id, vpc_details):
    """
    Associate a VPN endpoint with private subnets
    :param vpn_endpoint_id:
    :param vpc_details:
    """
    # associate the VPN with subnets in different AZs (the VPN can't be associated with multiple
    # subnets in the same AZ)
    seen_azs = []
    subnet_ids = []

    existing_associations = _get_subnet_associations(vpn_endpoint_id=vpn_endpoint_id)
    associated_subnet_ids = [x['TargetNetworkId'] for x in existing_associations]

    for subnet in vpc_details['Subnets']:
        az = subnet['AvailabilityZone']
        if az in seen_azs:
            continue

        subnet_id = subnet['SubnetId']

        seen_azs.append(az)

        if subnet_id in associated_subnet_ids:
            continue

        subnet_ids.append(subnet_id)

    for subnet_id in subnet_ids:
        command = '%s ec2 associate-client-vpn-target-network --client-vpn-endpoint-id=%s --subnet-id=%s' % (
            AWS, vpn_endpoint_id, subnet_id)
        logging.info("Executing command: %s" % command)
        subprocess.run(command, shell=True, check=True)


def _describe_vpc(vpc_id):
    """
    Returns details of the VPC's CIDR range and subnets
    :param vpc_id:
    :return: map
    """
    print("Describing VPC '%s'" % vpc_id)
    command = '%s ec2 describe-vpcs --vpc-ids=%s' % (AWS, vpc_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())
    vpc_data = response["Vpcs"][0]
    logging.info("Description of VPC '%s': %s" % (vpc_id, vpc_data))

    print("Describing subnets for VPC '%s'" % vpc_id)
    command = '%s ec2 describe-subnets --filters=Name=vpc-id,Values=%s' % (AWS, vpc_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())
    vpc_data['Subnets'] = response['Subnets']

    return vpc_data


def _get_vpn_endpoint(cluster_name):
    """
    Returns the ID of a VPN endpoint if it exists
    :param cluster_name:
    :return: ID of the VPN endpoint if it exists
    """
    # filtering is half-baked so we need to manually filter ourselves
    command = '%s ec2 describe-client-vpn-endpoints' % (AWS)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    endpoints = json.loads(result.stdout.decode("utf-8").strip())

    logging.info("Endpoint data is: %s", endpoints)

    endpoint_name = _get_endpoint_name(cluster_name)

    for endpoint in endpoints['ClientVpnEndpoints']:
        if endpoint['Description'] == endpoint_name:
            return endpoint['ClientVpnEndpointId']

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
        raise RuntimeError("Failed to get VPC '%s': %s" % (vpc_name, result))

    result = result.stdout.decode("utf-8").strip()
    if result == 'None':
        result = None

    logging.debug("Returning result '%s'" % result)

    return result


def _export_config_file(endpoint_id, cluster_name, cert_path, key_path, output_dir):
    """
    Exports the OpenVPN config file and modifies it
    :param endpoint_id: AWS endpoint ID
    :param cluster_name: Name of the cluster
    :param cert_path: Path to the client certificate
    :param key_path: Path to the client private key
    :return: Path to the written output file
    """
    timestamp = int(time.time())
    dest_path = os.path.join(output_dir, "%s-vpn-%d.ovpn" % (cluster_name, timestamp))

    print("Exporting client config file")
    command = '%s ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id %s --output text' % (
        AWS, endpoint_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    config = result.stdout.decode("utf-8").strip()

    # append the cert and key
    with open(cert_path) as f:
        cert = f.read().strip()

    with open(key_path) as f:
        key = f.read().strip()

    config = """
%s

<cert>
%s
</cert>

<key>
%s
</key>    
""" % (config, cert, key)

    # prepend a string to the DNS name
    random_str = uuid.uuid4().hex[:12]
    config = config.replace('remote ', 'remote %s.' % random_str)

    print("OVPN config file written to: %s" % dest_path)

    with open(dest_path, 'w') as f:
        f.write(config)

    return dest_path


def _create_vpn_endpoint(cert_arns, cluster_name, vpc_details):
    """
    Returns the endpoint ID
    :param cert_arns:
    :param cluster_name:
    :param vpc_details: A map of VPC data as returned by describe-vpcs
    :return:
    """
    print("Creating VPN endpoint...")

    cidr_block = vpc_details['CidrBlock']

    # naively calculate the default nameserver address (2 above the base of the CIDR block)
    cidr_parts = cidr_block.split('/')
    ip = cidr_parts[0]
    ip_parts = ip.split('.')
    ip_parts[3] = str(int(ip_parts[3]) + 2)
    ns_ip = '.'.join(ip_parts)

    logging.info("Default nameserver IP for CIDR '%s' is '%s'" % (cidr_block, ns_ip))

    command = '%s ec2 create-client-vpn-endpoint --client-cidr-block %s --server-certificate-arn %s ' \
              '--authentication-options %s --connection-log-options Enabled=false --dns-servers %s ' \
              '--description "%s" ' \
              '--tag-specifications \'ResourceType=client-vpn-endpoint,Tags=[{Key=Name,Value="%s"}]\'' % (
        AWS,
        '10.1.0.0/16',              # cidr block for client IPs
        cert_arns[SERVER],
        'Type=certificate-authentication,MutualAuthentication={ClientRootCertificateChainArn=%s}' % cert_arns[CLIENT],
        ns_ip,
        _get_endpoint_name(cluster_name),
        _get_endpoint_name(cluster_name))
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    response = json.loads(result.stdout.decode("utf-8").strip())
    endpoint_id = response['ClientVpnEndpointId']
    print("Created VPN Endpoint '%s'" % endpoint_id)
    return endpoint_id


def _get_cert_name(cluster_name, actor):
    """
    Returns a tag name for a certificate
    :param cluster_name: Cluster name
    :param actor: e.g. client, server
    :return: string
    """
    return '%s VPN %s cert' % (cluster_name, actor)


def _get_endpoint_name(cluster_name):
    """
    Returns the name of a VPN for the given cluster
    :param cluster_name: Cluster name
    :return: string
    """
    return '%s VPN' % cluster_name


def _get_certs(cluster_name):
    """
    Searches for VPN certs for the named cluster
    :param cluster_name:
    :return: a map of cert arns
    """
    arns = {}

    logging.info("Searching for existing VPN certs for cluster '%s'" % cluster_name)

    # tags we're looking for
    server_tag_value = _get_cert_name(cluster_name=cluster_name, actor=SERVER)
    client_tag_value = _get_cert_name(cluster_name=cluster_name, actor=CLIENT)

    # first we need to list the certificates
    command = '%s acm list-certificates' % AWS
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    cert_json = result.stdout.decode("utf-8").strip()
    certs = json.loads(cert_json)

    # get the tags for each cert and try to match them up with either CLIENT or SERVER
    for cert in certs['CertificateSummaryList']:
        arn = cert['CertificateArn']
        command = '%s acm list-tags-for-certificate --certificate-arn=%s' % (AWS, arn)
        logging.info("Executing command: %s" % command)
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        logging.info("Got output: %s" % result)
        tags = json.loads(result.stdout.decode("utf-8").strip())

        for tag in tags['Tags']:
            if tag['Key'] == 'Name':
                if tag['Value'] == server_tag_value:
                    arns[SERVER] = arn
                    continue
                elif tag['Value'] == client_tag_value:
                    arns[CLIENT] = arn
                    continue

    if arns:
        logging.info("Found existing cert arns: %s" % arns)
    else:
        logging.info("No existing certs found")

    return arns


def _import_certs(out_dir, cluster_name):
    """
    Imports certs into AWS using the CLI. We don't use terraform because it doesn't support adding tags to certs and
    we should do that
    :param out_dir:
    """
    arns = {}

    for actor in [CLIENT, SERVER]:
        command = '%s acm import-certificate --certificate file://%s/%s.pem --private-key file://%s/%s-key.pem ' \
                  '--certificate-chain file://%s/ca.pem --output=text' %(AWS, out_dir, actor, out_dir, actor, out_dir)
        logging.info("Executing command in %s: %s" % (out_dir, command))
        print("Importing %s certs to AWS..." % actor)
        result = subprocess.run(command, shell=True, check=True, cwd=out_dir, capture_output=True)
        logging.info("Got output: %s" % result)
        arns[actor] = result.stdout.decode("utf-8").strip()

        print("Tagging cert in AWS...")
        tag_value = _get_cert_name(cluster_name=cluster_name, actor=actor)
        command = '%s acm add-tags-to-certificate --certificate-arn=%s --tags=Key=Name,Value="%s"' % (
            AWS, arns[actor], tag_value)
        subprocess.run(command, shell=True, check=True)

    print("Successfully imported and tagged certs: ")
    for k, v in arns.items():
        print('='.join([k, v]))

    print()
    return arns


def _generate_certs(cluster_name, cert_json, out_dir, hostnames=""):
    """
    Generates certs & keys for a CA, client and server
    :param cluster_name: Single word name of the cluster (for namespacing)
    :param hostnames: Hostnames to add to the client/server certs
    """
    cert_json = os.path.abspath(cert_json)

    # generate CA certs
    command = '%s gencert -initca -cn="%s VPN CA" %s | %s -bare ca' % (CFSSL, cluster_name, cert_json, CFSSL_JSON)
    logging.info("Executing command in %s: %s" % (out_dir, command))
    print("Generating CA certs")
    subprocess.run(command, shell=True, check=True, cwd=out_dir)

    # generate client/server certs
    for actor in [CLIENT, SERVER]:
        # command = '%s gencert -initca -cn="%s VPN CA" %s | %s -bare ca' % (CFSSL, cluster_name, cert_json, CFSSL_JSON)
        command = '%s gencert -ca=ca.pem -cn="%s VPN %s" -hostname="%s" -ca-key=%s %s | %s -bare %s' % (
            CFSSL,
            cluster_name,
            actor,
            hostnames,
            os.path.join(out_dir, "ca-key.pem"),
            cert_json,
            CFSSL_JSON,
            actor)
        logging.info("Executing command in %s: %s" % (out_dir, command))
        print("Generating %s certs" % actor)
        subprocess.run(command, shell=True, check=True, cwd=out_dir)


if __name__=="__main__":
    sys.exit(main())
