#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_mallet.sh"
	echo "    Download and set up tree-based topic modeling software (by Yuening et al.)."
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

function __setup_treetm__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/tree-tm
	TOOLS_SUBPATH=$TOOLS_PATH/tree-tm

	echo "# Downloading TreeTM..."
	if [ ! -f "$EXTERNALS_SUBPATH/tree-tm.zip" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		curl --insecure --location http://www.cs.umd.edu/~ynhu/code/tree-TM.zip > $EXTERNALS_SUBPATH/tree-tm.zip
		
		echo "    Extracting TreeTM readme..."
		unzip $EXTERNALS_SUBPATH/tree-tm.zip tree-TM/readme.txt -d $EXTERNALS_SUBPATH &&\
			mv $EXTERNALS_SUBPATH/tree-TM/readme.txt $EXTERNALS_SUBPATH/README &&\
			rmdir $EXTERNALS_SUBPATH/tree-TM
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/tree-tm.zip"
	fi
	echo

	echo "# Setting up TreeTM..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing TreeTM..."
		unzip $EXTERNALS_SUBPATH/tree-tm.zip -d $TOOLS_SUBPATH &&\
			mv $TOOLS_SUBPATH/tree-TM/* $TOOLS_SUBPATH &&\
			rmdir $TOOLS_SUBPATH/tree-TM
		
		echo "    Compiling TreeTM..."
		PWD=`pwd`
		cd $TOOLS_SUBPATH
		mkdir class
		javac -cp class:lib/* src/cc/mallet/topics/*/*.java -d class
		cd $PWD
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $TOOLS_PATH
__setup_treetm__
