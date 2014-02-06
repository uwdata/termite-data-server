#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_gensim.sh"
	echo "    Download and set up gensim."
	echo "    This script should be run from the root of the git repo."
	echo
	echo "    Gensim is not downloaded by default."
	echo "    This script assumes that easy_install is available,"
	echo "    and that SciPy and NumPy are already installed."
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

function __setup_gensim__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/gensim-0.8.9
	TOOLS_SUBPATH=$TOOLS_PATH/gensim-0.8.9
	SYMLINK_SUBPATH=$TOOLS_PATH/gensim
	SYMLINK=gensim-0.8.9
	
	echo "# Downloading gensim..."
	if [ ! -f "$EXTERNALS_SUBPATH/gensim-0.8.9.tar.gz" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		echo "    Downloading source code..."
		curl --insecure --location http://pypi.python.org/packages/source/g/gensim/gensim-0.8.9.tar.gz > $EXTERNALS_SUBPATH/gensim-0.8.9.tar.gz

		echo "    Extracting gensim README..."
		tar -zxf $EXTERNALS_SUBPATH/gensim-0.8.9.tar.gz gensim-0.8.9/README.rst &&\
			mv gensim-0.8.9/README.rst README &&\
			rmdir gensim-0.8.9
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/gensim-0.8.9.tar.gz"
	fi
	echo
	
	echo "# Setting up gensim..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing..."
		tar -zxf $EXTERNALS_SUBPATH/gensim-0.8.9.tar.gz gensim-0.8.9 &&\
			mv gensim-0.8.9/* $TOOLS_SUBPATH &&\
			ln -s $SYMLINK $SYMLINK_SUBPATH &&\
			rmdir gensim-0.8.9

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
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $TOOLS_PATH
__setup_gensim__
