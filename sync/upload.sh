#!/bin/bash

echo "rsync -ravz apps chuangca@jcchuang.org:workspace/TermiteDataServer_GitHub/"
rsync -ravz apps chuangca@jcchuang.org:workspace/TermiteDataServer_GitHub/

echo "rsync -ravz web2py/applications chuangca@jcchuang.org:workspace/TermiteDataServer_GitHub/web2py/"
rsync -ravz web2py/applications chuangca@jcchuang.org:workspace/TermiteDataServer_GitHub/web2py/
