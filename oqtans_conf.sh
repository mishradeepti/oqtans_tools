#!/bin/bash


export OQTANS_ROOT_PATH=/mnt/oqtansTools
export OQTANS_PATH=$OQTANS_ROOT_PATH/oqtans
export OQTANS_SRC_PATH=$OQTANS_ROOT_PATH/oqtans_src
export OQTANS_DEP_PATH=$OQTANS_ROOT_PATH/oqtans_dep
export OQTANS_PYTHON_VERSION=2.6

export OQTANS_TMP_PATH=$OQTANS_ROOT_PATH/tmp
mkdir -p $OQTANS_TMP_PATH

export PYTHONPATH=${OQTANS_DEP_PATH}/lib/python${OQTANS_PYTHON_VERSION}/site-packages:${OQTANS_DEP_PATH}/lib64/python${OQTANS_PYTHON_VERSION}/site-packages
export LD_LIBRARY_PATH=$OQTANS_DEP_PATH/lib:$OQTANS_DEP_PATH/lib64:$LD_LIBRARY_PATH
export PATH=$OQTANS_DEP_PATH/bin:$OQTANS_DEP_PATH/octave/bin:$PATH
