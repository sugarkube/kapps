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

variable "db_engine" {
  description = "E.g. mysql, postgres, etc."
}

variable "db_engine_mode" {
  description = "E.g. serverless, etc."
}

variable "master_username" {
  description = "Username of the master DB user"
}

variable "master_password" {
  description = "Password for the master DB user"
}

variable "skip_final_snapshot" {
  description = "Whether to take a final snapshot when the cluster is deleted"
  default = false
}

variable "max_capacity" {
  description = "Max DB capacity when using the serverless engine mode"
  default = 2
}

variable "min_capacity" {
  description = "min DB capacity when using the serverless engine mode"
  default = 1
}

variable "auto_pause_seconds" {
  description = "The time, in seconds, before an Aurora DB cluster in serverless mode is paused"
  default = 300
}

variable "timeout_action" {
  description = "The action to take when the timeout is reached"
  default = "ForceApplyCapacityChange"
}
