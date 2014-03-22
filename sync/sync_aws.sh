#!/bin/bash

SERVER="termite.aws.jcchuang.org"

for APP in init infovis_mallet infovis_gensim poliblogs_mallet poliblogs_gensim poliblogs_stm 20newsgroups_mallet fomc_mallet fomc_gensim fomc_stm nsf1k_mallet nsf10k_mallet nsf25k_mallet
do
	echo "rsync -rvz --copy-links --copy-dirlinks web2py/applications/$APP root@$SERVER:/var/www/web2py/applications"
	rsync -rvz --copy-links --copy-dirlinks web2py/applications/$APP root@$SERVER:/var/www/web2py/applications
done
