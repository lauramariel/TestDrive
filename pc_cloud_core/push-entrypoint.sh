#!/bin/bash

echo "Taring up directory:"
tar -zcvf entrypoint.tar.gz entrypoint
echo "Copying to GCP bucket"
gsutil cp entrypoint.tar.gz gs://testdrive-templates/pc-cloud-core/entrypoint.tar.gz
echo "Removing tarball"
rm entrypoint.tar.gz