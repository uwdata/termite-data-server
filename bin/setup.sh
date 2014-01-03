#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools

function __create_folder__ {
	FOLDER=$1
	if [ ! -d $FOLDER ]
	then
		echo "Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __setup_mallet__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/mallet-2.0.7
	TOOLS_SUBPATH=$TOOLS_PATH/mallet-2.0.7

	if [ ! -f "$EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH

		echo ">> Downloading MALLET (MAchine Learning for LanguagE Toolkit)..."
		curl --insecure --location http://mallet.cs.umass.edu/dist/mallet-2.0.7.tar.gz > $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz
	else
		echo ">> Downloading MALLET (MAchine Learning for LanguagE Toolkit)..."
		echo "    Already downloaded: $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz"
	fi

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH
		
		echo ">> Uncompressing MALLET..."
		tar -zxvf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7 &&\
			mv mallet-2.0.7/* $TOOLS_SUBPATH &&\
			rmdir mallet-2.0.7

		echo ">> Extracting MALLET License..."
		cp $TOOLS_SUBPATH/LICENSE $EXTERNALS_SUBPATH/LICENSE
	else
		echo ">> Setting up MALLET..."
		echo "    Already available: $TOOLS_SUBPATH"
	fi
}

function __setup_web2py__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/web2py
	TOOLS_SUBPATH=$TOOLS_PATH/web2py

	if [ ! -f "$EXTERNALS_SUBPATH/web2py_src.zip" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH
		
		echo ">> Downloading web2py..."
		curl --insecure --location http://www.web2py.com/examples/static/web2py_src.zip > $EXTERNALS_SUBPATH/web2py_src.zip
	else
		echo ">> Downloading web2py..."
		echo "    Already downloaded: $EXTERNALS_SUBPATH/web2py_src.zip"
	fi

	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH
		
		echo ">> Uncompressing web2py..."
		unzip $EXTERNALS_SUBPATH/web2py_src.zip web2py/* -d $TOOLS_SUBPATH &&\
		mv $TOOLS_SUBPATH/web2py/* $TOOLS_SUBPATH/ &&\
		rmdir $TOOLS_SUBPATH/web2py
		
		echo ">> Extracting web2py License..."
		unzip $EXTERNALS_SUBPATH/web2py_src.zip web2py/LICENSE -d $EXTERNALS_SUBPATH &&\
		mv $EXTERNALS_SUBPATH/web2py/LICENSE $EXTERNALS_SUBPATH/ &&\
		rmdir $EXTERNALS_SUBPATH/web2py

		echo ">> Removing 'no password, no web admin interface' dialogue box..."
		sed -i bkp "s/self.error('no password, no web admin interface')/pass #self.error('no password, no web admin interface')/g" $TOOLS_SUBPATH/gluon/widget.py

	else
		echo ">> Setting up web2py..."
		echo "    Already available: $TOOLS_SUBPATH"
	fi
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $TOOLS_PATH
__setup_mallet__
__setup_web2py__
