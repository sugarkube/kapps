# AWS Aurora DB
This kapp creates a serverless AWS Aurora DB for use during development. It's launched into the same VPC as the Kubernetes cluster that will use it. 

In production it'd probably be better to create a dedicated VPC to launch it into and peer it with the cluster's VPC.
