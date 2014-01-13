#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools
APPS_PATH=apps

if [ $# -lt 1 ] || [ $1 != "DELETE" ]
then
	echo "Usage: bin/unsetup.sh DELETE"
	echo "    Remove downloaded content, tools, and web server."
	echo "    This script should be run from the root of the git repo."
	echo "    WARNING: This will remove all applications on the web server!"
	echo
	exit -1
fi

echo "# Removing all downloaded content..."
rm -rfv $EXTERNALS_PATH
echo

echo "# Removing all tools..."
rm -rfv $TOOLS_PATH
echo

echo "# Removing web server and all web applications..."
rm -rfv $APPS_PATH
echo
