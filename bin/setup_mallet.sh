#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_mallet.sh"
	echo "    Download and set up MALLET topic modeling toolkit."
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

function __create_folder__ {
	FOLDER=$1
	TAB=$2
	if [ ! -d $FOLDER ]
	then
		echo "${TAB}Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __setup_mallet__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/mallet-2.0.7
	TOOLS_SUBPATH=$TOOLS_PATH/mallet-2.0.7

	echo "# Downloading MALLET (MAchine Learning for LanguagE Toolkit)..."
	if [ ! -f "$EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		curl --insecure --location http://mallet.cs.umass.edu/dist/mallet-2.0.7.tar.gz > $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz"
	fi
	echo

	echo "# Setting up MALLET..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing MALLET..."
		tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7 &&\
			mv mallet-2.0.7/* $TOOLS_SUBPATH &&\
			rmdir mallet-2.0.7

		echo "    Extracting MALLET License..."
		cp $TOOLS_SUBPATH/LICENSE $EXTERNALS_SUBPATH/LICENSE
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $TOOLS_PATH
__setup_mallet__
