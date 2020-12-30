# How to Run

1. Change config.json to match your cluster info
2. In the same directory, run:

export CUSTOM_SCRIPT_CONFIG=$(cat config.json | tr '\n' ' ' | tr -s ' ')

3. Then run the script you want or entrypoint.sh to run them all

Once everything is done and ready to go, push the tarball with push-entrypoint.sh for use in nx-on-gcp specs