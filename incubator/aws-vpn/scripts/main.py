#!/usr/bin/env python3
#
# This script creates a VPN Endpoint (generating all required certificates) and downloads an OpenVPN config file to
# access the endpoint.
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

    create_vpn_endpoint(cert_arns=cert_arns,
                        cluster_name=cluster_name)


def create_vpn_endpoint(cert_arns, cluster_name):
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
