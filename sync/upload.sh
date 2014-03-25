#!/bin/bash

SERVER="chuangca@jcchuang.org"
OPTIONS="-ravz --exclude-from=sync/exclude.txt"

for FOLDER in apps landing_src server_src
do
	echo "rsync $OPTIONS $FOLDER $SERVER:workspace/TermiteDataServer_GitHub/"
	rsync $OPTIONS $FOLDER $SERVER:workspace/TermiteDataServer_GitHub/
done
