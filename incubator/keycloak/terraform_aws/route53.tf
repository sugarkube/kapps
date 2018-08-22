data "aws_route53_zone" "zone" {
  name = "${local.cluster_hosted_zone}"
}

resource "aws_route53_record" "record" {
  name    = "${var.release}"
  type    = "CNAME"
  ttl     = "${var.dns_ttl}"
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  records = []
}
