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

function __setup_web2py__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/web2py

	echo "# Setting up web2py..."
	if [ ! -d "$WEB2PY_PATH" ]
	then

		if [ ! -d "$EXTERNALS_SUBPATH" ]
		then
			mkdir -p $EXTERNALS_PATH
			mkdir -p $EXTERNALS_SUBPATH
			echo "    Downloading..."
			curl --insecure --location http://www.web2py.com/examples/static/web2py_src.zip > $EXTERNALS_SUBPATH/web2py_src.zip
			echo "    Extracting license..."
			unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/LICENSE -d $EXTERNALS_SUBPATH &&\
				mv $EXTERNALS_SUBPATH/web2py/LICENSE $EXTERNALS_SUBPATH/ &&\
				rmdir $EXTERNALS_SUBPATH/web2py
		else
			echo "    Already downloaded: $EXTERNALS_SUBPATH/web2py_src.zip"
		fi

		mkdir -p $WEB2PY_PATH
		echo "    Uncompressing..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/* -d $WEB2PY_PATH &&\
			mv $WEB2PY_PATH/web2py/* $WEB2PY_PATH/ &&\
			rmdir $WEB2PY_PATH/web2py
		
		echo "    Removing 'no password, no web admin interface' dialogue box..."
		sed -i bkp "s/self.error('no password, no web admin interface')/pass #self.error('no password, no web admin interface')/g" $WEB2PY_PATH/gluon/widget.py

		echo "    Removing unused apps..."
		rm -rf $WEB2PY_PATH/applications/welcome
		rm -rf $WEB2PY_PATH/applications/examples
		rm -rf $WEB2PY_PATH/examples
		rm -rf $WEB2PY_PATH/handlers
		
		echo "    Copying FastCGI setup..."
		cp web2py_src/* $WEB2PY_PATH/
		cp web2py_src/.htaccess $WEB2PY_PATH/
		
		if [ ! -d $APPS_PATH ]
		then
			echo "    Creating $APPS_PATH folder..."
			mkdir $APPS_PATH
		fi

		if [ ! -d $APPS_PATH/init ]
		then
			echo "    Creating the default app..."
			mkdir $APPS_PATH/init
			touch $APPS_PATH/init/__init__.py
			ln -s ../../landing_src/views $APPS_PATH/init/views
			ln -s ../../landing_src/models $APPS_PATH/init/models
			ln -s ../../landing_src/controllers $APPS_PATH/init/controllers
			ln -s ../../landing_src/modules $APPS_PATH/init/modules
			ln -s ../../landing_src/static $APPS_PATH/init/static
			ln -s ../init $APPS_PATH/welcome
		fi
		
		if [ ! -d $WEB2PY_PATH/applications-original ]
		then
			echo "    Linking to $APPS_PATH folder..."
			mv $WEB2PY_PATH/applications $WEB2PY_PATH/applications-original
			ln -s ../$APPS_PATH/ $WEB2PY_PATH/applications
			ln -s ../$WEB2PY_PATH/applications-original/admin/ $APPS_PATH/admin
		fi
	else
		echo "    Already available: $WEB2PY_PATH"
	fi
	echo
}

__setup_web2py__
