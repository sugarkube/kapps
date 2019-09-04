variable "prefix" {
  description = "Short prefix. Used in identifiers for namespacing. Allows this to be used multiple times in a stack"
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

variable "master_username" {
  description = "Username of the master DB user"
}

// the master password should be provided as a variable, or ideally be pulled from a secret store
variable "master_password" {
  description = "Password for the master DB user"
  default     = null
}

variable "skip_final_snapshot" {
  description = "Whether to take a final snapshot when the cluster is deleted"
  default     = false
}

variable "max_capacity" {
  description = "Max DB capacity when using the serverless engine mode"
  default     = 2
}

variable "min_capacity" {
  description = "min DB capacity when using the serverless engine mode"
  default     = 1
}

variable "auto_pause_seconds" {
  description = "The time, in seconds, before an Aurora DB cluster in serverless mode is paused"
  default     = 300
}

variable "timeout_action" {
  description = "The action to take when the timeout is reached"
  default     = "ForceApplyCapacityChange"
}

// these need to come from an EKS/Kops cluster to permit it to access the DB
// todo - can we just query for them directly using the cluster name?
variable "vpc_security_group_ids" {
  type        = "list"
  description = "List of VPC security groups to associate with the Cluster"
  default     = null
}

variable "database_name" {
  description = "Name of a database to create"
}

variable "worker_sg_tag" {
  description = "Name of a tag associated with a security group attached to worker nodes"
}

variable "worker_sg_value" {
  description = "Value of the tag associated with security group attached to worker nodes to select them by"
}
