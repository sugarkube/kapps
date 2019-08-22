// this is generically named so it makes sense if we add support for e.g. azure, gce, etc.
output "bucket_encryption_key" {
  value       = "${aws_kms_key.key.arn}"
  description = "ID of the key used to encrypt data in the bucket"
}
