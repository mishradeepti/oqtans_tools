#!/bin/bash
set -e
pwd
cd $OQTANS_PATH/ASP_0.3
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$OQTANS_DEP_PATH/lib/
export PYTHONPATH=$PYTHONPATH:$OQTANS_DEP_PATH/lib/python2.6/site-packages/:$OQTANS_DEP_PATH/lib/python2.6/dist-packages/

if [ "$3" = "spf1" ]
then
	if [ "${10}" = "yes" ]
	then 
 		./asp $1 --organism=$2 -t -s $5
	else
 		./asp $1 --organism=$2 -s $5
	fi
elif [ "$3" = "gff2" ]
then
	if [ "${10}" = "yes" ]
	then
 		./asp $1 --organism=$2 -t -g $4
	else
 		./asp $1 --organism=$2 -g $4
	fi
elif [ "$3" = "binary" ]
then
	mkdir -p $6/pred
	echo "This dataset contains acceptor splice site predictions in binary SPF format (for use with mGene, Palmapper, QPALMA)" > $7
	mkdir -p $8/pred
	echo "This dataset contains donor splice site predictions in binary SPF format (for use with mGene, Palmapper, QPALMA)" > $9
 	if [ "${10}" = "yes" ]
	then 
		./asp $1 --organism=$2 -t -b $6
	else 
		./asp $1 --organism=$2 -b $6
	fi
	mv $6/acc/* $6/pred/
	rmdir $6/acc
	mv $6/don/* $8/pred
	rmdir $6/don
fi
