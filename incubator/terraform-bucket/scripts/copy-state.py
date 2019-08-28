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
    print("Running in %s mode" % mode)
    if mode == INSTALL:
        return install(backend_path)
    elif mode == DELETE:
        return delete(backend_path)


def _get_remote_backend(backend_path):
    "Returns the remote bucket and state file path from a backend.tf file"
    with open(backend_path) as f:
        contents = f.read()

    bucket = re.search(r'bucket\s*=\s*"([^"]+)"', contents)
    bucket = bucket.group(1)
    key = re.search(r'key\s*=\s*"([^"]+)"', contents)
    key = key.group(1)
    print("Extracted bucket='%s', key='%s' from %s" % (bucket, key, backend_path))
    return (bucket, key)


def install(backend_path):
    tf_dir = os.path.dirname(backend_path)
    print("Terraform directory: %s" % tf_dir)

    bucket, path = _get_remote_backend(backend_path)

    # check whether the state bucket exists
    result = subprocess.run([AWS, "s3", "ls", "s3://%s" % bucket])
    if result.returncode == 0:
        print("Bucket '%s' exists" % bucket)

        state_file = os.path.join(tf_dir, STATE_FILE)
        if os.path.exists(state_file):
            state_file_s3_path = "s3://%s/%s" % (bucket, path)
            result = subprocess.run([AWS, "s3", "cp", state_file, state_file_s3_path])
            if result.returncode == 0:
                print("State file copied to %s. Deleting local copy" % state_file_s3_path)
                os.unlink(state_file)
            else:
                raise RuntimeError("Error copying state file to %s" % state_file_s3_path)

        if not backend_path.endswith('.tf'):
            correct_backend_path = backend_path + ".tf"
            print("Renaming %s to %s" % (backend_path, correct_backend_path))
            os.rename(backend_path, correct_backend_path)

    else:
        print("Bucket '%s' doesn't exist" % bucket)


def delete(backend_path):
    pass


if __name__=="__main__":
    sys.exit(main())
