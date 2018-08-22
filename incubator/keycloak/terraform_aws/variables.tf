variable "project" {
  description = "Short, single-word name of the project. Used in identifiers for namespacing."
}

variable "release" {
  description = "Release name. Used for namespacing."
}

variable "cluster" {
  description = "Unique per cluster. Allows multiple clusters per cloud-provider account. Used for namespacing."
}

variable "region" {
  description = "AWS region name. Used for namespacing global resources."
}

variable "hosted_zone" {
  description = "Hosted zone to create DNS records under"
}

variable "db_engine" {
  description = "E.g. mysql, postgres, etc."
}

variable "db_engine_version" {
  description = "DB version"
}

variable "db_instance_class" {
  description = "Size of instance to use, e.g. db.t2.micro, etc."
}

variable "db_port" {
  description = "Database port"
}

variable "db_allocated_storage" {
  description = "Database allocated storage"
}

variable "db_storage_type" {
  description = "Database storage type"
  default     = "gp2"
}

variable "db_storage_encrypted" {
  description = "Whether to encrypt DB storage or not"
  default     = "true"
}

variable "db_parameter_group_name" {
  description = "Database parameter group name."
}

variable "db_password" {
  description = "Database password."
}

variable "db_username" {
  description = "Database username."
}

variable "dns_ttl" {
  description = "TTL for the DNS record."
  default     = "300"
}
