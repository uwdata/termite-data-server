#!/bin/bash

EXTERNALS_PATH=externals
APPS_PATH=apps

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_web2py.sh"
	echo "    Download and set up web2py framework."
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

function __setup_web2py__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/web2py
	TOOLS_SUBPATH=web2py

	echo "# Downloading web2py..."
	if [ ! -d "$EXTERNALS_SUBPATH" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		curl --insecure --location http://www.web2py.com/examples/static/web2py_src.zip > $EXTERNALS_SUBPATH/web2py_src.zip

		echo "    Extracting license..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/LICENSE -d $EXTERNALS_SUBPATH &&\
			mv $EXTERNALS_SUBPATH/web2py/LICENSE $EXTERNALS_SUBPATH/ &&\
			rmdir $EXTERNALS_SUBPATH/web2py
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/web2py_src.zip"
	fi
	echo

	echo "# Setting up web2py..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/* -d $TOOLS_SUBPATH &&\
			mv $TOOLS_SUBPATH/web2py/* $TOOLS_SUBPATH/ &&\
			rmdir $TOOLS_SUBPATH/web2py
		
		echo "    Removing 'no password, no web admin interface' dialogue box..."
		sed -i bkp "s/self.error('no password, no web admin interface')/pass #self.error('no password, no web admin interface')/g" $TOOLS_SUBPATH/gluon/widget.py
		
		echo "    Removing unused apps and example files..."
		rm -rf $TOOLS_SUBPATH/applications/welcome
		rm -rf $TOOLS_SUBPATH/applications/examples
		rm -rf $TOOLS_SUBPATH/examples
		rm -rf $TOOLS_SUBPATH/handlers
		
		__create_folder__ $TOOLS_SUBPATH/applications/init "    "
		echo "    Creating the default app..."
		touch $TOOLS_SUBPATH/applications/init/__init__.py
		ln -s ../../../landing_src/views $TOOLS_SUBPATH/applications/init/views
		ln -s ../../../landing_src/models $TOOLS_SUBPATH/applications/init/models
		ln -s ../../../landing_src/controllers $TOOLS_SUBPATH/applications/init/controllers
		ln -s ../../../landing_src/modules $TOOLS_SUBPATH/applications/init/modules
		ln -s ../../../landing_src/static $TOOLS_SUBPATH/applications/init/static
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $APPS_PATH
__setup_web2py__
