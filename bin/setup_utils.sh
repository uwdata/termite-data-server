#!/bin/bash

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_utils.sh"
	echo "    Compile helper programs."
	echo
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

cd utils/mallet && make
