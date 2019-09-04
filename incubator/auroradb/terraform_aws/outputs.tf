output "master_password" {
  value = "${random_password.password.result}"
}

output "endpoint" {
  value = "${aws_rds_cluster.db.endpoint}"
}

output "port" {
  value = "${aws_rds_cluster.db.port}"
}
