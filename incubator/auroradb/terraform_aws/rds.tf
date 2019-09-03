resource "random_password" "password" {
  length = 16
  special = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

locals {
  identifer = "${var.project}-${replace(var.cluster, ".", "-")}"
}

resource "aws_rds_cluster" "postgresql" {
  cluster_identifier = "${local.identifer}"
  engine = "${var.db_engine}"
  engine_mode = "serverless"
  master_username = "${var.master_username}"
  master_password = "${var.master_password != null ? var.master_password : random_password.password.result}"
  skip_final_snapshot = "${var.skip_final_snapshot}"

  scaling_configuration {
    auto_pause               = true
    max_capacity             = "${var.max_capacity}"
    min_capacity             = "${var.min_capacity}"
    seconds_until_auto_pause = "${var.auto_pause_seconds}"
    timeout_action           = "${var.timeout_action}"
  }

  tags = {
    Cluster = "${var.cluster}"
  }
}
