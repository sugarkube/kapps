output "name_servers" {
  value = "${aws_route53_zone.public_hosted_zone.name_servers}"
}
