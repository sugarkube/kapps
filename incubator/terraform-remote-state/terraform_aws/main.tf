resource "aws_kms_key" "key" {
  description             = "Key for Terraform state for ${var.cluster}"
  deletion_window_in_days = 10
}

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
        kms_master_key_id = "${aws_kms_key.key.arn}"
        sse_algorithm = "aws:kms"
      }
    }
  }
}
