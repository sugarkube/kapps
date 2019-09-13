data "aws_route53_zone" "zone" {
  name         = "${var.hosted_zone}"
  private_zone = "${var.private_zone}"
}

resource "aws_route53_record" "alert_manager_record" {
  count   = var.alert_manager_record_name == "" ? 0 : 1
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  name    = "${var.alert_manager_record_name}"
  type    = "CNAME"
  ttl     = "${var.ttl}"
  records = ["${var.cname_hostname}"]
}

resource "aws_route53_record" "grafana_record" {
  count   = var.grafana_record_name == "" ? 0 : 1
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  name    = "${var.grafana_record_name}"
  type    = "CNAME"
  ttl     = "${var.ttl}"
  records = ["${var.cname_hostname}"]
}

resource "aws_route53_record" "prometheus_record" {
  count   = var.prometheus_dns_record_name == "" ? 0 : 1
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  name    = "${var.prometheus_dns_record_name}"
  type    = "CNAME"
  ttl     = "${var.ttl}"
  records = ["${var.cname_hostname}"]
}
