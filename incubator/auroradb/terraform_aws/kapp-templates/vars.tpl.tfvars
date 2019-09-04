database_name = "{{ .kapp.vars.database_name }}"
worker_sg_value = "{{ .kapp.vars.worker_sg_value }}"
cluster = "{{ .stack.cluster }}"
prefix = "{{ .kapp.vars.database_name }}"     // just use the database name to keep things simple
region = "{{ .stack.region }}"
