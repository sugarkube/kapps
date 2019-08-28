resource "aws_kms_key" "key" {
  description             = "Key for Terraform state for ${var.cluster}"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "bucket" {
  bucket = "${var.bucket_name}"
  acl    = "private"

  tags = {
    Name      = "${var.bucket_name}"
    Cluster   = "${var.cluster}"
    Sugarkube = "true"
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.key.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = "${aws_s3_bucket.bucket.id}"

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

// this fails when used with the above public access block
//resource "aws_s3_bucket_policy" "deny_unencrypted_uploads" {
//  bucket = "${aws_s3_bucket.bucket.id}"
//  policy = <<POLICY
//{
//   "Version":"2012-10-17",
//   "Id":"PutObjPolicy",
//   "Statement":[{
//         "Sid":"DenyUnEncryptedObjectUploads",
//         "Effect":"Deny",
//         "Principal":"*",
//         "Action":"s3:PutObject",
//         "Resource":"${aws_s3_bucket.bucket.arn}/*",
//         "Condition":{
//            "StringNotEquals":{
//               "s3:x-amz-server-side-encryption":"aws:kms"
//            }
//         }
//      }
//   ]
//}
//POLICY
//}