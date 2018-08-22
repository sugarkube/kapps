output "db_host" {
  value = "${aws_db_instance.db.address}"
}

output "db_port" {
  value = "${var.db_port}"
}

output "hostname" {
  value = "${var.release}.${local.cluster_hosted_zone}"
}
