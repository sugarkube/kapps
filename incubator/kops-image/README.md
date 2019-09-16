# Overview
This kapp downloads the latest Kops image ID for the given region and makes Sugarkube load it as a provider file.

The process (as defined in the `sugarkube.yaml` file) is as follows:

1. Use `wget` to download the contents of a URL to a local file
1. Tell sugarkube to load any defined outputs. Since the previously written file is defined as an output, the contents are loaded and are referenceable. 
1. Sugarkube then generates templates - the template in this kapp refers to the contents of the previously loaded output.
1. The kapp also contains an instruction to make Sugarkube add the rendered template to its list of provider vars files, which means that the YAML will be merged with the other YAMLs for kops.
