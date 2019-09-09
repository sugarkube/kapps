data "aws_route53_zone" "zone" {
  name = "${var.hosted_zone}"
}

resource "aws_route53_record" "record" {
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  name    = "${var.dns_record_name}"
  type    = "CNAME"
  ttl     = "${var.ttl}"
  records = ["${var.cname_hostname}"]
}
