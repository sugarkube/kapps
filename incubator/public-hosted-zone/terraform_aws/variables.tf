variable "hosted_zone" {
  description = "Name of the hosted zone to create"
}

variable "parent_hosted_zone" {
  description = "Name of the parent hosted zone to create NS records in"
}

variable "region" {
  description = "AWS region to use"
}

variable "ns_ttl" {
  description = "TTL of NS records"
  default     = 30
}