#!/bin/bash

EXTERNALS_PATH=externals
TOOLS_PATH=tools
APPS_PATH=apps

function __create_folder__ {
	FOLDER=$1
	TAB=$2
	if [ ! -d $FOLDER ]
	then
		echo "${TAB}Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __setup_mallet__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/mallet-2.0.7
	TOOLS_SUBPATH=$TOOLS_PATH/mallet-2.0.7

	echo "# Downloading MALLET (MAchine Learning for LanguagE Toolkit)..."
	if [ ! -f "$EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		curl --insecure --location http://mallet.cs.umass.edu/dist/mallet-2.0.7.tar.gz > $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz"
	fi
	echo

	echo "# Setting up MALLET..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing MALLET..."
		tar -zxf $EXTERNALS_SUBPATH/mallet-2.0.7.tar.gz mallet-2.0.7 &&\
			mv mallet-2.0.7/* $TOOLS_SUBPATH &&\
			rmdir mallet-2.0.7

		echo "    Extracting MALLET License..."
		cp $TOOLS_SUBPATH/LICENSE $EXTERNALS_SUBPATH/LICENSE
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

function __setup_web2py__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/web2py
	TOOLS_SUBPATH=$TOOLS_PATH/web2py

	echo "# Downloading web2py..."
	if [ ! -f "$EXTERNALS_SUBPATH/web2py_src.zip" ]
	then
		__create_folder__ $EXTERNALS_SUBPATH "    "
		curl --insecure --location http://www.web2py.com/examples/static/web2py_src.zip > $EXTERNALS_SUBPATH/web2py_src.zip
	else
		echo "    Already downloaded: $EXTERNALS_SUBPATH/web2py_src.zip"
	fi
	echo

	echo "# Setting up web2py..."
	if [ ! -d "$TOOLS_SUBPATH" ]
	then
		__create_folder__ $TOOLS_SUBPATH "    "
		echo "    Uncompressing web2py..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/* -d $TOOLS_SUBPATH &&\
		mv $TOOLS_SUBPATH/web2py/* $TOOLS_SUBPATH/ &&\
		rmdir $TOOLS_SUBPATH/web2py
		
		echo "    Extracting web2py License..."
		unzip -q $EXTERNALS_SUBPATH/web2py_src.zip web2py/LICENSE -d $EXTERNALS_SUBPATH &&\
		mv $EXTERNALS_SUBPATH/web2py/LICENSE $EXTERNALS_SUBPATH/ &&\
		rmdir $EXTERNALS_SUBPATH/web2py

		echo "    Removing 'no password, no web admin interface' dialogue box..."
		sed -i bkp "s/self.error('no password, no web admin interface')/pass #self.error('no password, no web admin interface')/g" $TOOLS_SUBPATH/gluon/widget.py
		
		__create_folder__ $TOOLS_SUBPATH/applications/termite "    "
		echo "    Setting up a default app..."
		ln -s ../../../../landing_src/controllers $TOOLS_SUBPATH/applications/termite/controllers
		ln -s ../../../../landing_src/views $TOOLS_SUBPATH/applications/termite/views
		ln -s ../../../../landing_src/static $TOOLS_SUBPATH/applications/termite/static
		sed -i bkp "s/redirect(URL('welcome', 'default', 'index'))/redirect(URL('termite', 'default', 'index'))/g" $TOOLS_SUBPATH/gluon/main.py
	else
		echo "    Already available: $TOOLS_SUBPATH"
	fi
	echo
}

__create_folder__ $EXTERNALS_PATH
__create_folder__ $TOOLS_PATH
__create_folder__ $APPS_PATH
__setup_mallet__
__setup_web2py__
