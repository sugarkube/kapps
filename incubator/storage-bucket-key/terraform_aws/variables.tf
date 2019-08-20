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