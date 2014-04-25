#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ]
then
	echo "Usage: bin/setup_treetm.sh"
	echo "    Download and set up tree-based topic modeling software (by Yuening et al.)."
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

function __setup_treetm__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/treetm
	TOOLS_SUBPATH=$TOOLS_PATH/treetm

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		echo "# Setting up interactive topic modeling..."

		if [ ! -f "$EXTERNALS_SUBPATH" ]
		then
			echo "    Creating folder '$EXTERNALS_SUBPATH'..."
			mkdir -p $EXTERNALS_PATH
			mkdir -p $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://www.cs.umd.edu/~ynhu/code/tree-TM.zip > $EXTERNALS_SUBPATH/tree-tm.zip
			echo "    Extracting README..."
			unzip $EXTERNALS_SUBPATH/tree-tm.zip tree-TM/readme.txt -d $EXTERNALS_SUBPATH &&\
				mv $EXTERNALS_SUBPATH/tree-TM/readme.txt $EXTERNALS_SUBPATH/README &&\
				rmdir $EXTERNALS_SUBPATH/tree-TM
		fi
		echo

		echo "    Creating folder '$TOOLS_SUBPATH'..."
		mkdir -p $TOOLS_PATH
		mkdir -p $TOOLS_SUBPATH
		echo "    Uncompressing..."
		unzip -q $EXTERNALS_SUBPATH/tree-tm.zip -d $TOOLS_SUBPATH &&\
			mv $TOOLS_SUBPATH/tree-TM/* $TOOLS_SUBPATH &&\
			rm -rf $TOOLS_SUBPATH/__MACOSX &&\
			rmdir $TOOLS_SUBPATH/tree-TM
		echo "    Compiling..."
		cd $TOOLS_SUBPATH &&\
			mkdir class &&\
			javac -cp class:lib/* src/cc/mallet/topics/*/*.java -d class

		echo "    Available: $TOOLS_SUBPATH"
		echo
	else
		echo "    Available: $TOOLS_SUBPATH"
	fi
}

__setup_treetm__
