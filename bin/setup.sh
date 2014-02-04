#!/bin/bash

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup.sh"
	echo "    Download and set up basic tools for Termite Web Server."
	echo "      - MALLET topic modeling toolkit"
	echo "      - Web2py framework"
	echo
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

bin/setup_web2py.sh
bin/setup_mallet.sh
