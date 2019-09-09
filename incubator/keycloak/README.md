# Keycloak

Since this is just an example we won't create an RDS database. However, in reality in prod you'd probably want to create one outside of an ephemeral cluster so it could be used by different clusters. Keeping state out of your clusters makes using ephemeral clusters simpler.

## Usage
This kapp relies on nginx ingress to proxy traffic. To access Keycloak after installing this kapp on Minikube, do the following:

  1. Get the nodeport that nginx-ingress is running on with e.g. `minikube service -n nginx1 nginx1-nginx-ingress-controller`
  1. The output of the above command should be a table containing an entry like `http://192.168.99.112:32446` under the URL column.
  1. Edit `/etc/hosts` to include the ingress hostname of this kapp and the above IP, e.g. if this kapp's ingress hostname is `keycloak.localhost`, for the above output you'd add an entry `keycloak.localhost   192.168.99.112` to `/etc/hosts`.
  1. Now use the port number from above to access the site, e.g.: `https://keycloak.localhost:32446`. You'll have to accept the self-signed cert, but now you'll be accessing Keycloak through nginx, just as you would when hosted in the Cloud.
  

## Password
After installation using the settings in this kapp, retrieve the 
randomly-generated admin password by running:
```
kubectl get secret --namespace keycloak keycloak-http -o jsonpath="{.data.password}" | base64 --decode; echo
```
The default username is `admin`.

**Note**: Make sure to change the password to prevent anyone who can run the 
above from gaining admin.
