#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ]
then
	echo "Usage: bin/setup_stmt.sh"
	echo "    Download and set up Stanford Topic Modeling Toolbox."
	echo "    This script should be run from the root of the git repo."
	echo
	exit -1
fi

function __setup_stmt__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/stmt-0.4.0
	TOOLS_SUBPATH=$TOOLS_PATH/stmt-0.4.0
	SYMLINK_SUBPATH=$TOOLS_PATH/stmt
	SYMLINK=stmt-0.4.0

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		echo "# Setting up STMT (Stanford Topic Modeling Toolkit)..."

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			echo "    Creating folder '$EXTERNALS_SUBPATH'..."
			mkdir -p $EXTERNALS_PATH
			mkdir -p $EXTERNALS_SUBPATH
			echo "    Downloading source code..."
			curl --insecure --location http://nlp.stanford.edu/software/tmt/tmt-0.4/tmt-0.4.0-src.zip > $EXTERNALS_SUBPATH/tmt-0.4.0-src.zip
			echo "    Extracting license..."
			unzip $EXTERNALS_SUBPATH/tmt-0.4.0-src.zip LICENSE -d $EXTERNALS_SUBPATH
			echo "You may delete downloaded files in this folder without affecting the topic model server." > $EXTERNALS_SUBPATH/safe-to-delete.txt
		fi

		echo "    Creating folder '$TOOLS_SUBPATH'..."
		mkdir -p $TOOLS_PATH
		mkdir -p $TOOLS_SUBPATH
		echo "    Downloading compiled binary..."
		curl --insecure --location http://nlp.stanford.edu/software/tmt/tmt-0.4/tmt-0.4.0.jar > $TOOLS_SUBPATH/tmt-0.4.0.jar
		ln -s $SYMLINK $SYMLINK_SUBPATH

		echo "    Available: $TOOLS_SUBPATH"
		echo
	else
		echo "    Available: $TOOLS_SUBPATH"
	fi
}

__setup_stmt__
