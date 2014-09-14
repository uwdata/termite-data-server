#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools
VERSION=0.9.1

if [ ! -d "bin" ]
then
	echo "Usage: bin/setup_gensim.sh"
	echo "    Download and set up gensim."
	echo "    This script should be run from the root of the git repo."
	echo
	echo "    Requires: easy_install, scipy, numpy"
	echo "    Running this script requires root access"
	echo
	exit -1
fi

function __setup_gensim__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/gensim-$VERSION
	TOOLS_SUBPATH=$TOOLS_PATH/gensim-$VERSION
	SYMLINK_SUBPATH=$TOOLS_PATH/gensim
	SYMLINK=gensim-$VERSION

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		echo "# Setting up gensim..."

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			echo "    Creating folder '$EXTERNALS_SUBPATH'..."
			mkdir -p $EXTERNALS_PATH
			mkdir -p $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://pypi.python.org/packages/source/g/gensim/gensim-$VERSION.tar.gz > $EXTERNALS_SUBPATH/gensim-$VERSION.tar.gz
			echo "    Extracting README..."
			tar -zxf $EXTERNALS_SUBPATH/gensim-$VERSION.tar.gz gensim-$VERSION/README.rst &&\
				mv gensim-$VERSION/README.rst $EXTERNALS_SUBPATH &&\
				rmdir gensim-$VERSION
			echo "You may delete downloaded files in this folder without affecting the topic model server." > $EXTERNALS_SUBPATH/safe-to-delete.txt
		fi
		
		echo "    Creating folder '$TOOLS_SUBPATH'..."
		mkdir -p $TOOLS_PATH
		mkdir -p $TOOLS_SUBPATH
		echo "    Uncompressing..."
		tar -zxf $EXTERNALS_SUBPATH/gensim-$VERSION.tar.gz gensim-$VERSION &&\
			mv gensim-$VERSION/* $TOOLS_SUBPATH &&\
			rmdir gensim-$VERSION &&\
			ln -s $SYMLINK $SYMLINK_SUBPATH

		echo "    Running self tests..."
		echo "python $TOOLS_SUBPATH/setup.py test"
		python $TOOLS_SUBPATH/setup.py test
		
		echo "    Installing..."
		echo "sudo python $TOOLS_SUBPATH/setup.py install"
		sudo python $TOOLS_SUBPATH/setup.py install
		
		echo "    Cleaning up..."
		echo "sudo rm -rf build/"
		sudo rm -rf build/
		echo "sudo rm -rf gensim.egg-info/"
		sudo rm -rf gensim.egg-info/
		echo "sudo rm -rf dist/"
		sudo rm -rf dist/

		echo "    Available: $TOOLS_SUBPATH"
		echo
	else
		echo "    Available: $TOOLS_SUBPATH"
	fi
}

__setup_gensim__
