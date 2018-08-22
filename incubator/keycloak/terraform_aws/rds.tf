resource "aws_db_instance" "db" {
  identifier           = "${local.short_identifier}"
  allocated_storage    = "${var.db_allocated_storage}"
  storage_type         = "${var.db_storage_type}"
  storage_encrypted    = "${var.db_storage_encrypted}"
  engine               = "${var.db_engine}"
  engine_version       = "${var.db_engine_version}"
  instance_class       = "${var.db_instance_class}"
  name                 = "${var.release}"
  username             = "${var.db_username}"
  password             = "${var.db_password}"
  parameter_group_name = "${var.db_parameter_group_name}"
  port                 = "${var.db_port}"
}
