#!/bin/bash

echo "rsync -ravz apps chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/"
rsync -ravz apps chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/

echo "rsync -ravz data chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/"
rsync -ravz data chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/

echo "rsync -ravz web2py/applications chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/web2py/"
rsync -ravz web2py/applications chuangca@jcchuang.org:workspace/TermiteTreeTM_GitHub/web2py/
