# Update region and zone in templates for testing

REGION="us-west1"
ZONE="us-west1-c"

case $1 in
    -r | --reverse )
    if [[ -z $2 ]]
    then
        echo "Please specify the spec you want to update"
    else
        echo "Updating spec $2 to add templatized fields"
        sed -i "" "s/$ZONE/{{ zone }}/g" $2
        sed -i "" "s/$REGION/{{ region }}/g" $2
    fi
    ;;
    *.json )
        echo "Updating spec $1 to $REGION and $ZONE"
    ;;
    * )
        echo "Please specify a spec"
esac

