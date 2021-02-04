#!/bin/bash

echo "Taring up directory:"
tar -zcvf entrypoint.tar.gz entrypoint
echo "Copying to GCP bucket $BUCKET"
gsutil cp entrypoint.tar.gz gs://testdrive-templates/clusters/entrypoint.tar.gz
echo "Removing tarball"
rm entrypoint.tar.gz
