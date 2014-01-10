#!/bin/bash

APPS_PATH=apps

if [ $# -lt 2 ]
then
	echo "Usage: `basename $0` model_folder app_identifier"
	echo
	exit -1
fi

MODEL_FOLDER=$1
APP_IDENTIFIER=$2
WEB2PY_ROOT=tools/web2py
WEB2PY_REL=../..

echo "# Importing a topic model as a web2py application: [$MODEL_FOLDER] --> [$APP_IDENTIFIER]"

if [ ! -d "$APPS_PATH/$APP_IDENTIFIER" ]
then
	echo "    Creating app folder: [$APPS_PATH/$APP_IDENTIFIER]"
	mkdir $APPS_PATH/$APP_IDENTIFIER

	echo "    Preparing app data: [$MODEL_FOLDER] --> [$APPS_PATH/$APP_IDENTIFIER/data]"
	bin/ImportMallet.py $MODEL_FOLDER $APPS_PATH/$APP_IDENTIFIER

	echo "    Setting up app subfolders: [$APPS_PATH/$APP_IDENTIFIER/controllers, views, static]"
	ln -s ../../server_src/controllers $APPS_PATH/$APP_IDENTIFIER/controllers
	ln -s ../../server_src/views $APPS_PATH/$APP_IDENTIFIER/views
	ln -s ../../server_src/static $APPS_PATH/$APP_IDENTIFIER/static

	if [ ! -e "$WEB2PY_ROOT/applications/$APP_IDENTIFIER" ]
	then
		echo "    Adding app to web2py server: [$APP_IDENTIFIER]"
		ln -s $WEB2PY_REL/../$APPS_PATH/$APP_IDENTIFIER $WEB2PY_ROOT/applications/$APP_IDENTIFIER
	fi
else
	echo "    Already exists: $APPS_PATH/$APP_IDENTIFIER"
fi

echo
