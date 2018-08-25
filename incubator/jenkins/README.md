# Jenkins

## Installation
**Note**: Check the Makefile for additional env vars that need setting, e.g.:
* HOSTED_ZONE - the domain name to create subdomain for this kapp, 
  e.g. `example.com`

### Local installation
When running against a local provider, no AWS resources will be created. Use
the following to install locally:
```
PROVIDER=local APPROVED=true make install
``` 

Add the Minikube cluster IP to `/etc/hosts`:
```
echo $(minikube ip) jenkins.localhost | sudo tee -a /etc/hosts
```

Then go to `https://jenkins.localhost`.

## Usage
After installation using the settings in this kapp, retrieve the 
randomly-generated admin password by running:
```
kubectl -n jenkins get secret jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode; echo
```
The default username is `admin`.

**Note**: Make sure to change the password to prevent anyone who can run the 
above from gaining admin.
