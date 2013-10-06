#!/bin/bash
#
# oqtans sub module compile program 
#
set -e 

source ../../oqtans_config.sh

cd $OQTANS_PATH/mTIM/0.2/src/utils
if [ "$1" == "" -o "$1" == "all" ];
then
    make octave
fi

if [ "$1" == "clean" ];
then
    make clean
fi
