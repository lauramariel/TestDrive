#!/bin/bash

echo "Taring up directory:"
tar -zcvf entrypoint-test.tar.gz entrypoint
echo "Copying to GCP bucket $BUCKET"
gsutil cp entrypoint-test.tar.gz gs://testdrive-templates/filesv3/deepdive/entrypoint-test.tar.gz
echo "Removing tarball"
rm entrypoint-test.tar.gz
