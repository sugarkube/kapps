#!/usr/bin/env python3
#
# This script creates a VPN Endpoint (generating all required certificates) and downloads an OpenVPN config file to
# access the endpoint.
#
# For the process, see https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-getting-started.html
#

import argparse
import subprocess
import sys
import logging
import os

logging.basicConfig(level=logging.DEBUG)

AWS=os.getenv("AWS", "aws")       # path to the AWS CLI binary
CFSSL=os.getenv("CFSSL", "cfssl")       # path to the cfssl binary
CFSSL_JSON=os.getenv("CFSSL_JSON", "cfssljson")       # path to the cfssljson binary

CLIENT="client"
SERVER="server"

def main():
    parser = argparse.ArgumentParser(description='Creates/updates hosted zones for kops.')
    parser.add_argument(dest='cluster_name', help='Name of the cluster')
    parser.add_argument('--hostnames', help='Common names to set in the client & server certificates (comma-separated)', default="")
    parser.add_argument('--out-dir', help='Path to the directory to write files to', default='../cfssl/_generated_certs')
    parser.add_argument('--cert-json', help='Path to a cfssl JSON file', default='../cfssl/cert.json')

    args = parser.parse_args()

    cluster_name = args.cluster_name

    out_dir = args.out_dir
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    generate_certs(cluster_name=cluster_name,
                   cert_json=args.cert_json,
                   out_dir=out_dir,
                   hostnames=args.hostnames)

    cert_arns = import_certs(out_dir=out_dir,
                             cluster_name=cluster_name)

    endpoint_id = create_vpn_endpoint(cert_arns=cert_arns,
                                      cluster_name=cluster_name)

    # todo - associate the endpoint with the private subnets

    cert_path = os.path.join(out_dir, "%s.pem" % CLIENT)
    key_path = os.path.join(out_dir, "%s-key.pem" % CLIENT)

    export_config_file(endpoint_id=endpoint_id,
                       cluster_name=cluster_name,
                       cert_path=cert_path,
                       key_path=key_path,
                       output_dir="~/Downloads")


def export_config_file(endpoint_id, cluster_name, cert_path, key_path, output_dir):
    """
    Exports the OpenVPN config file and modifies it
    :param endpoint_id: AWS endpoint ID
    :param cluster_name: Name of the cluster
    :param cert_path: Path to the client certificate
    :param key_path: Path to the client private key
    :return: Path to the written output file
    """
    dest_path = os.path.join(output_dir, "%s-vpn.ovpn" % cluster_name)

    if os.path.exists(dest_path):
        print("Config file already downloaded")
        return dest_path

    print("Exporting client config file")
    command = '%s ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id %s --output text' % (
        AWS, endpoint_id)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)
    config = result.stdout.decode("utf-8").strip()

    # append the cert and key
    with open(cert_path) as f:
        cert = f.read()

    with open(key_path) as f:
        key = f.read()

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
    config = config.replace('remote ', 'remote blah99.')

    print("Writing downloaded (and modified) config file to %s" % dest_path)

    with open(dest_path, 'w') as f:
        f.write(config)

    return dest_path


def create_vpn_endpoint(cert_arns, cluster_name):
    """
    Returns the endpoint ID
    :param cert_arns:
    :param cluster_name:
    :return:
    """
    print("Creating VPN endpoint...")
    command = '%s ec2 create-client-vpn-endpoint --client-cidr-block %s --server-certificate-arn %s ' \
              '--authentication-options %s --connection-log-options Enabled=false --dns-servers %s ' \
              '--split-tunnel --description "%s" ' \
              '--tag-specifications \'ResourceType=client-vpn-endpoint,Tags=[{Key=Name,Value="%s"}]\'' % (
        AWS,
        '172.20.0.0/16',                # todo - grab the correct CIDR range for the VPC
        cert_arns[SERVER],
        'Type=certificate-authentication,MutualAuthentication={ClientRootCertificateChainArn=%s}' % cert_arns[CLIENT],
        '172.20.0.2',                   # todo - grab the correct CIDR range for the VPC
        "%s VPN" % cluster_name,
        "%s VPN" % cluster_name)
    logging.info("Executing command: %s" % command)
    result = subprocess.run(command, shell=True, check=True, capture_output=True)
    logging.info("Got output: %s" % result)


def import_certs(out_dir, cluster_name):
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
        command = '%s acm add-tags-to-certificate --certificate-arn=%s --tags=Key=Name,Value="%s VPN %s cert"' % (
            AWS, arns[actor], cluster_name, actor)
        subprocess.run(command, shell=True, check=True)

    print("Successfully imported and tagged certs: ")
    for k, v in arns.items():
        print('='.join([k, v]))

    print()
    return arns


def generate_certs(cluster_name, cert_json, out_dir, hostnames=""):
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
