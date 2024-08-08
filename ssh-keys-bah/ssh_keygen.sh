#!/bin/sh

echo "Enter keyfile name"
read keyname
ssh-keygen -C "" -t rsa -b 4096 -f `pwd`/$keyname.pem
