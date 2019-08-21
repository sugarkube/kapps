resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_name}"
  acl = "private"

  tags = {
    Name = "${var.bucket_name}"
    Cluster = "${var.cluster}"
    Sugarkube = "true"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${var.encryption_key_id}"
        sse_algorithm = "aws:kms"
      }
    }
  }
}
