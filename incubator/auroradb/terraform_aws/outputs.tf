output "master_password" {
  value = "${random_password.password.result}"
}

output "endpoint" {
  value = "${aws_rds_cluster.db.endpoint}"
}

output "master_user" {
  value = "${var.master_username}"
}

output "database" {
  value = "${var.database_name}"
}
