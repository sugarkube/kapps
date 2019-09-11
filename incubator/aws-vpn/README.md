# Overview
This kapp creates a VPN endpoint to a target VPC and all required certificates. It then downloads an OpenVPN config file that can be used to connect to it. The VPN can be used to access services running in a VPC that aren't exposed to the Internet.

This script uses a script to create and query AWS resources instead of using Terraform because Terraform doesn't support various API calls we need so instead this script shells out to the AWS CLI directly. 

## Requirements
This uses [cfssl](https://github.com/cloudflare/cfssl) to generate the certs required to set up a VPN on AWS.

Install `cfssl` with:

* OSX: `brew install cfssl`
* Ubuntu: `sudo apt install golang-cfssl` 

This script also requires the AWS CLI. See the [installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).
