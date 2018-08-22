locals {
  basename            = "${var.project}-${var.cluster}"
  long_identifier     = "${local.basename}-${var.release}-${var.region}"
  short_identifier    = "${local.basename}-${var.release}"
  cluster_hosted_zone = "${var.cluster}.${var.hosted_zone}"
}
