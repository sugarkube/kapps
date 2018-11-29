resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_name}"
  acl    = "private"
}

// todo - create a kapp that creates KMS keys and enable server-side encryption on this bucket