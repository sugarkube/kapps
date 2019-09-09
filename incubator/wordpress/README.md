# Usage
This kapp relies on nginx ingress to proxy traffic. To access Wordpress after installing this kapp on Minikube, do the following:

  1. Get the nodeport that nginx-ingress is running on with e.g. `minikube service -n nginx1 nginx1-nginx-ingress-controller`
  1. The output of the above command should be a table containing an entry like `http://192.168.99.112:32446` under the URL column.
  1. Edit `/etc/hosts` to include the ingress hostname of this kapp and the above IP, e.g. if this kapp's ingress hostname is `site1.localhost`, for the above output you'd add an entry `site1.localhost   192.168.99.112` to `/etc/hosts`.
  1. Now use the port number from above to access the site, e.g.: `https://site.localhost:32446`. You'll have to accept the self-signed cert, but now you'll be accessing Wordpress through nginx, just as you would when hosted in the Cloud.
  