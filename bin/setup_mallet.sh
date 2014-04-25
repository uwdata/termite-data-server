#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ]
then
	echo "Usage: bin/setup_mallet.sh"
	echo "    Download and set up MALLET topic modeling toolkit."
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

function __setup_mallet__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/mallet-2.0.7
	TOOLS_SUBPATH=$TOOLS_PATH/mallet-2.0.7
	SYMLINK_SUBPATH=$TOOLS_PATH/mallet
	SYMLINK=mallet-2.0.7

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		echo "# Setting up MALLET (MAchine Learning for LanguagE Toolkit)..."

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			echo "    Creating folder '$EXTERNALS_SUBPATH'..."
			mkdir -p $EXTERNALS_PATH
			mkdir -p $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://mallet.cs.umass.edu/dist/mallet-2.0.7.tar.gz > $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz
			echo "    Extracting license..."
			tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7/LICENSE &&\
				mv mallet-2.0.7/LICENSE $EXTERNALS_SUBPATH &&\
				rmdir mallet-2.0.7
			echo "You may delete downloaded files in this folder without affecting the topic model server." > $EXTERNALS_SUBPATH/safe-to-delete.txt
		fi

		echo "    Creating folder '$TOOLS_SUBPATH'..."
		mkdir -p $TOOLS_PATH
		mkdir -p $TOOLS_SUBPATH
		echo "    Uncompressing..."
		tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7 &&\
			mv mallet-2.0.7/* $TOOLS_SUBPATH &&\
			ln -s $SYMLINK $SYMLINK_SUBPATH &&\
			rmdir mallet-2.0.7

		echo "    Available: $TOOLS_SUBPATH"
		echo
	else
		echo "    Available: $TOOLS_SUBPATH"
	fi
}

__setup_mallet__
