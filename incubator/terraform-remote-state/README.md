# To do
The Makefile should:
1. Abort if there's no `terraform_<provider>` directory
1. Check if the target bucket exists
1. If it does, just rename _generated_backend.tf.tmp -> _generated_backend.tf
1. If not, run terraform, then copy the state into the bucket under an 
   appropriate prefix 