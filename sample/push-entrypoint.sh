#!/bin/bash

BUCKET=$(git branch | grep \* | awk '{print $NF}')

if [ $BUCKET == "master" ]
then
    echo "In master so let's name the bucket after the cwd"
    BUCKET=$(pwd | awk -F/ '{print $NF}')
fi
 
echo "Taring up directory:"
tar -zcvf entrypoint.tar.gz entrypoint
echo "Copying to GCP bucket $BUCKET"
gsutil cp entrypoint.tar.gz gs://testdrive-templates/dev/$BUCKET/entrypoint.tar.gz
echo "Removing tarball"
rm entrypoint.tar.gz