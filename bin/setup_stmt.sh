#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_stmt.sh"
	echo "    Download and set up Stanford Topic Modeling Toolbox."
	echo "    This script should be run from the root of the git repo."
	echo
	echo "    STMT is not downloaded by default."
	echo
	exit -1
fi

function __setup_stmt__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/stmt-0.4.0
	TOOLS_SUBPATH=$TOOLS_PATH/stmt-0.4.0
	SYMLINK_SUBPATH=$TOOLS_PATH/stmt
	SYMLINK=stmt-0.4.0

	echo "# Setting up STMT (Stanford Topic Modeling Toolkit)..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then

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
		else
			echo "    Already downloaded: $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz"
		fi

		echo "    Creating folder '$TOOLS_SUBPATH'..."
		mkdir -p $TOOLS_PATH
		mkdir -p $TOOLS_SUBPATH
		echo "    Downloading compiled binary..."
		curl --insecure --location http://nlp.stanford.edu/software/tmt/tmt-0.4/tmt-0.4.0.jar > $TOOLS_SUBPATH/tmt-0.4.0.jar
		ln -s $SYMLINK $SYMLINK_SUBPATH
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__setup_stmt__
