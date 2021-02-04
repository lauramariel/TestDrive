#!/bin/bash
set -ex

# Generate the SSH keys in the default location
ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa
