#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_stm.sh"
	echo "    Download and set up Structural Topic Models."
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi
