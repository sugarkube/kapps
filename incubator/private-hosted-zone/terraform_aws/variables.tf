variable "cluster_name" {
  description = "Name of the cluster"
}

variable "parent_hosted_zone" {
  description = "Name of the parent hosted zone to create NS records in for the zone for this cluster"
}

variable "region" {
  description = "AWS region to use"
}

variable "ns_ttl" {
  description = "TTL of NS records"
  default = 30
}