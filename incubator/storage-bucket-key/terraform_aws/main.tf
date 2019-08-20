resource "aws_kms_key" "key" {
  description = "Key for ${var.cluster}"
  deletion_window_in_days = 10
  enable_key_rotation = true
}
