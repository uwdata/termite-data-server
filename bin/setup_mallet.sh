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
	if [ ! -d $FOLDER ]
	then
		echo "    Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __setup_mallet__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/mallet-2.0.7
	TOOLS_SUBPATH=$TOOLS_PATH/mallet-2.0.7
	SYMLINK_SUBPATH=$TOOLS_PATH/mallet
	SYMLINK=mallet-2.0.7

	echo "# Setting up MALLET (MAchine Learning for LanguagE Toolkit)..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			__create_folder__ $EXTERNALS_PATH
			__create_folder__ $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://mallet.cs.umass.edu/dist/mallet-2.0.7.tar.gz > $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz
			echo "    Extracting license..."
			tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7/LICENSE &&\
				mv mallet-2.0.7/LICENSE $EXTERNALS_SUBPATH &&\
				rmdir mallet-2.0.7
			echo "You may delete downloaded files in this folder without affecting the topic model server." > $EXTERNALS_SUBPATH/safe-to-delete.txt
		else
			echo "    Already downloaded: $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz"
		fi

		__create_folder__ $TOOLS_PATH
		__create_folder__ $TOOLS_SUBPATH
		echo "    Uncompressing..."
		tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7 &&\
			mv mallet-2.0.7/* $TOOLS_SUBPATH &&\
			ln -s $SYMLINK $SYMLINK_SUBPATH &&\
			rmdir mallet-2.0.7
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__setup_mallet__
