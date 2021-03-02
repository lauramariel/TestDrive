#!/bin/bash

cat entrypoint/entrypoint.sh
echo "Taring up directory:"
tar -zcvf entrypoint.tar.gz entrypoint
echo "Copying to GCP bucket $BUCKET"
gsutil -h "Cache-Control:no-cache,max-age=0" cp entrypoint.tar.gz gs://testdrive-templates/filesv3/deepdive/
echo "Removing tarball"
rm entrypoint.tar.gz
