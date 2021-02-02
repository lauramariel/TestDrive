# Update region and zone in templates for testing

REGION="us-west1"
ZONE="us-west1-b"

if [[ -z $1 ]]
then
  echo "Please specify the spec file to update"
else
  echo "Updating spec $1 to $REGION and $ZONE"
  sed -i "" "s/{{ region }}/$REGION/g" $1
  sed -i "" "s/{{ zone }}/$ZONE/g" $1
fi
