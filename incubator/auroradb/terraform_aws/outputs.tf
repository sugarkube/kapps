output "master_password" {
  value = "${random_password.password.result}"
}