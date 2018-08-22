# Keycloak

## Installation

### Local installation
When running against a local provider, no AWS resources will be created. Use
the following to install locally:
```
PROVIDER=local APPROVED=true make install
``` 

### AWS installation
Installing onto an AWS Kubernetes cluster will create an RDS database. The size
of the instance will depend on the environment. E.g. to install using the dev
settings, first export your AWS credentials to the shell then run:
```
PROVIDER=aws APPROVED=false make install \
  tf-opts='-var-file=vars/defaults.tfvars -var-file=vars/dev.tfvars'
PROVIDER=aws APPROVED=true make install \
  tf-opts='-var-file=vars/defaults.tfvars -var-file=vars/dev.tfvars'
```
The first command will make Terraform plan its operations, and the second 
invocation will apply it.

## Usage
After installation, retrieve randomly-generated admin password by running:
```
kubectl get secret --namespace {{ .Release.Namespace }} {{ template "keycloak.fullname" . }}-http -o jsonpath="{.data.password}" | base64 --decode; echo
```
