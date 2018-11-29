locals {
  cluster_zone = "${var.cluster}.${var.parent_zone}"
}

resource "aws_route53_zone" "cluster_zone" {
  name = "${local.cluster_zone}"
}

data "aws_route53_zone" "parent_zone" {
  name = "${var.parent_zone}"
}

resource "aws_route53_record" "parent" {
  zone_id = "${data.aws_route53_zone.parent_zone.zone_id}"
  name    = "${local.cluster_zone}"
  type    = "NS"
  ttl     = "${var.ns_ttl}"

  records = [
    "${aws_route53_zone.cluster_zone.name_servers.0}",
    "${aws_route53_zone.cluster_zone.name_servers.1}",
    "${aws_route53_zone.cluster_zone.name_servers.2}",
    "${aws_route53_zone.cluster_zone.name_servers.3}",
  ]
}