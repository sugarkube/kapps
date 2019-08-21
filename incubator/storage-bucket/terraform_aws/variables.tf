variable "bucket_name" {
  description = "Name of the S3 bucket to create"
}

variable "cluster" {
  description = "Unique per cluster. Allows multiple clusters per cloud-provider account. Used for namespacing."
}

variable "encryption_key_id" {
  description = "KMS key ARN"
}
