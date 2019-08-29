#!/usr/bin/env python3

# This script is run before and after Terraform when the kapp is installed. Both times it does the following:
#
# * If the state bucket exists:
#   * If a local `terraform.tfstate` file exists, copy it into the bucket and delete it locally
#   * Rename the _generated_backend.tf.tmp file to _generated_backend.tf so it'll be used by Terraform
#
# This script is also run before the kapp is deleted to move the terraform state from the bucket to the local
# terraform directory, since Terraform won't delete a non-empty bucket, and to delete the _generated_backend.tf file
# so Terraform won't use it.
#

import argparse
import sys
import os
import re
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

INSTALL="install"
DELETE="delete"
STATE_FILE="terraform.tfstate"
AWS="aws"       # name of the aws CLI binary

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(dest='mode', choices=[INSTALL, DELETE], help='Mode to run in')
    parser.add_argument(dest='backend_path', help='Path to the backend file')

    args = parser.parse_args()
    return run(args.mode, args.backend_path)


def run(mode, backend_path):
    logging.info("Running in %s mode" % mode)
    if mode == INSTALL:
        return install(backend_path)
    elif mode == DELETE:
        return delete(backend_path)


def _get_remote_backend(backend_path):
    "Returns the remote bucket and state file path from a backend.tf file"
    if not os.path.exists(backend_path):
        raise FileNotFoundError("Backend path '%s' doesn't exist" % backend_path)

    with open(backend_path) as f:
        contents = f.read()

    bucket = re.search(r'bucket\s*=\s*"([^"]+)"', contents)
    bucket = bucket.group(1)
    key = re.search(r'key\s*=\s*"([^"]+)"', contents)
    key = key.group(1)
    logging.info("Extracted bucket='%s', key='%s' from %s" % (bucket, key, backend_path))
    return (bucket, key)


def install(backend_path):
    tf_dir = os.path.dirname(backend_path)
    logging.info("Terraform directory: %s" % tf_dir)

    try:
        bucket, path = _get_remote_backend(backend_path)
    except FileNotFoundError as e:
        logging.error(e)
        logging.info("This is nothing to worry about if the kapp is already installed and the backend "
                     "has already been copied.")
        return

    # check whether the state bucket exists
    result = subprocess.run([AWS, "s3", "ls", "s3://%s" % bucket])
    if result.returncode == 0:
        logging.info("Bucket '%s' exists" % bucket)

        state_file = os.path.join(tf_dir, STATE_FILE)
        if os.path.exists(state_file):
            state_file_s3_path = "s3://%s/%s" % (bucket, path)
            result = subprocess.run([AWS, "s3", "cp", state_file, state_file_s3_path])
            if result.returncode == 0:
                logging.info("State file copied to %s. Deleting local copy" % state_file_s3_path)
                os.unlink(state_file)
            else:
                raise RuntimeError("Error copying state file to %s" % state_file_s3_path)

        if not backend_path.endswith('.tf'):
            correct_backend_path = backend_path + ".tf"
            logging.info("Renaming %s to %s" % (backend_path, correct_backend_path))
            os.rename(backend_path, correct_backend_path)

    else:
        logging.info("Bucket '%s' doesn't exist" % bucket)


def delete(backend_path):
    tf_dir = os.path.dirname(backend_path)
    logging.info("Terraform directory: %s" % tf_dir)

    bucket, path = _get_remote_backend(backend_path)

    # check whether the remote state file exists
    state_file_s3_path = "s3://%s/%s" % (bucket, path)
    result = subprocess.run([AWS, "s3", "ls", state_file_s3_path])
    if result.returncode == 0:
        logging.info("Remote state file '%s' exists" % state_file_s3_path)
        local_state_file = os.path.join(tf_dir, STATE_FILE)

        result = subprocess.run([AWS, "s3", "mv", state_file_s3_path, local_state_file])
        if result.returncode == 0:
            logging.info("Remote state file '%s' moved to '%s'" % (state_file_s3_path, local_state_file))
        else:
            raise RuntimeError("Error moving moving remote state file '%s' to '%s'" % (state_file_s3_path,
                                                                                       local_state_file))

    backend_file = backend_path + ".tf"
    if os.path.exists(backend_file):
        logging.info("Deleting local backend file '%s'" % backend_file)
        os.unlink(backend_file)


if __name__=="__main__":
    sys.exit(main())
