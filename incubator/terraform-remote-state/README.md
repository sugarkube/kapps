# Description
This kapp creates an S3 bucket that can be used for Terraform remote state. After the bucket is created the local state file is copied into it. 

This isn't suitable for creating arbitrary S3 buckets - it's specifically tailored for Terraform.
