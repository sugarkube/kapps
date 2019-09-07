variable "region" {
  description = "AWS region name. Used for namespacing global resources."
}

variable "record_name" {
  description = "Non-fully-qualified name of the DNS record to create (e.g. 'site1')"
}

variable "cname_hostname" {
  description = "Hostname to CNAME the record to"
}

variable "hosted_zone" {
  description = "Name of the hosted zone to create the record in"
}

variable "ttl" {
  description = "TTL for the record"
  default     = 30
}
