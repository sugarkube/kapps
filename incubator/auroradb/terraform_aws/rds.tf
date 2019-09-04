resource "random_password" "password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

locals {
  identifer = "${var.project}-${replace(var.cluster, ".", "-")}"
}

data "aws_vpc" "cluster_vpc" {
  tags = {
    Name = "eksctl-${var.cluster}-cluster/VPC" # todo - take these from vars depending on whether it's kops/EKS
  }
}

data "aws_subnet_ids" "vpc_subnets" {
  vpc_id = "${data.aws_vpc.cluster_vpc.id}"
  tags = {
    "kubernetes.io/role/internal-elb" : 1 # todo - take these from vars depending on whether it's kops/EKS
  }
}

data "aws_security_group" "worker_security_groups" {
  vpc_id = "${data.aws_vpc.cluster_vpc.id}"
  tags = {
    "${var.worker_sg_tag}" : "${var.worker_sg_value}"
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "${local.identifer}"
  subnet_ids = data.aws_subnet_ids.vpc_subnets.ids

  tags = {
    Name    = "${local.identifer}"
    Cluster = "${var.cluster}"
  }
}

resource "aws_security_group" "rds" {
  name        = "RDS ${local.identifer}"
  description = "Allow RDS access"
  vpc_id      = "${data.aws_vpc.cluster_vpc.id}"

  tags = {
    Name = "${local.identifer} RDS"
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
    description = "Access within the RDS cluster"
  }

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = ["${data.aws_security_group.worker_security_groups.id}"]
    description     = "Access from K8s worker nodes"
  }
}

resource "aws_rds_cluster" "db" {
  cluster_identifier   = "${local.identifer}"
  engine               = "${var.db_engine}"
  engine_mode          = "serverless"
  master_username      = "${var.master_username}"
  master_password      = "${var.master_password != null ? var.master_password : random_password.password.result}"
  skip_final_snapshot  = "${var.skip_final_snapshot}"
  db_subnet_group_name = "${aws_db_subnet_group.default.name}"
  vpc_security_group_ids = [
  aws_security_group.rds.id]
  database_name = "${var.database_name}"

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
