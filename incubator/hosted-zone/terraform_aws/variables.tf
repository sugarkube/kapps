variable "cluster" {
  description = "Name of the cluster"
}

variable "parent_zone" {
  description = "Name of the parent hosted zone to create NS records in for the zone for this cluster"
}

variable "ns_ttl" {
  description = "TTL of NS records"
  default = 30
}