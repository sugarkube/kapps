data "aws_route53_zone" "parent_hosted_zone" {
  name = "${var.parent_hosted_zone}"
}

resource "aws_route53_zone" "public_hosted_zone" {
  name = "${var.hosted_zone}"
}

resource "aws_route53_record" "parent" {
  zone_id = "${data.aws_route53_zone.parent_hosted_zone.zone_id}"
  name    = "${var.hosted_zone}"
  type    = "NS"
  ttl     = "${var.ns_ttl}"

  records = [
    "${aws_route53_zone.public_hosted_zone.name_servers.0}",
    "${aws_route53_zone.public_hosted_zone.name_servers.1}",
    "${aws_route53_zone.public_hosted_zone.name_servers.2}",
    "${aws_route53_zone.public_hosted_zone.name_servers.3}",
  ]
}