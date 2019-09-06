# Public hosted zone
This kapp creates a public hosted zone and a wildcard ACM certificate for it. A script is also run to reduce NS record TTLs so that changes propagate faster when new clusters are created or deleted. 

Creating ACM certificates can sometimes take quite a while so it's better to run this as part of a stack with no cluster to prepare the environment. It could slow things down quite a lot if this kapp was on the critical path used to create and tear down clusters frequently. Clusters should create their own public hosted zones as subdomains of this one which should be much faster.
