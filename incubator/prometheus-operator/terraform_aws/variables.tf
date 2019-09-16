variable "region" {
  description = "AWS region name. Used for namespacing global resources."
}

variable "alert_manager_record_name" {
  description = "Non-fully-qualified name of the DNS record for Alert Manager"
  default     = ""
}

variable "grafana_record_name" {
  description = "Non-fully-qualified name of the DNS record for Grafana"
  default     = ""
}

variable "prometheus_dns_record_name" {
  description = "Non-fully-qualified name of the DNS record to create for prometheus. If blank, no DNS record will be created"
  default     = ""
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

variable "private_zone" {
  description = "Boolean indicating whether the zone to create a DNS record in is a private hosted zone or not"
}