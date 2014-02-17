#!/bin/bash

EXTERNALS_PATH=externals
WEB2PY_PATH=web2py
APPS_PATH=apps

if [ ! -d "server_src" ] || [ ! -d "landing_src" ]
then
	echo "Usage: bin/setup_web2py.sh"
	echo "    Download and set up the web2py framework."
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

function __setup_web2py__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/web2py

	echo "# Setting up web2py..."
	if [ ! -d "$WEB2PY_PATH" ]
	then

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			__create_folder__ $EXTERNALS_PATH
			__create_folder__ $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://www.web2py.com/examples/static/web2py_src.zip > $EXTERNALS_SUBPATH/web2py_src.zip
			echo "    Extracting license..."
			unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/LICENSE -d $EXTERNALS_SUBPATH &&\
				mv $EXTERNALS_SUBPATH/web2py/LICENSE $EXTERNALS_SUBPATH/ &&\
				rmdir $EXTERNALS_SUBPATH/web2py
		else
			echo "    Already downloaded: $EXTERNALS_SUBPATH/web2py_src.zip"
		fi

		__create_folder__ $APPS_PATH
		__create_folder__ $WEB2PY_PATH
		echo "    Uncompressing..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/* -d $WEB2PY_PATH &&\
			mv $WEB2PY_PATH/web2py/* $WEB2PY_PATH/ &&\
			rmdir $WEB2PY_PATH/web2py
		
		echo "    Removing 'no password, no web admin interface' dialogue box..."
		sed -i bkp "s/self.error('no password, no web admin interface')/pass #self.error('no password, no web admin interface')/g" $WEB2PY_PATH/gluon/widget.py
		
		echo "    Removing unused apps and example files..."
		rm -rf $WEB2PY_PATH/applications/welcome
		rm -rf $WEB2PY_PATH/applications/examples
		rm -rf $WEB2PY_PATH/examples
		rm -rf $WEB2PY_PATH/handlers
		
		__create_folder__ $WEB2PY_PATH/applications/init
		echo "    Creating the default app..."
		touch $WEB2PY_PATH/applications/init/__init__.py
		ln -s ../../../landing_src/views $WEB2PY_PATH/applications/init/views
		ln -s ../../../landing_src/models $WEB2PY_PATH/applications/init/models
		ln -s ../../../landing_src/controllers $WEB2PY_PATH/applications/init/controllers
		ln -s ../../../landing_src/modules $WEB2PY_PATH/applications/init/modules
		ln -s ../../../landing_src/static $WEB2PY_PATH/applications/init/static
		
		echo "    Copying FastCGI setup..."
		cp web2py_src/* $WEB2PY_PATH/
		cp web2py_src/.htaccess $WEB2PY_PATH/
	else
		echo "    Already available: $WEB2PY_PATH"
	fi
	echo
}

__setup_web2py__
