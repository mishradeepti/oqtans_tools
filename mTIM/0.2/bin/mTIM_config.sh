#!/bin/bash
export MTIM_VERSION=0.2
export MTIM_PATH=${OQTANS_PATH}/mTIM/0.2
export MTIM_SRC_PATH=${MTIM_PATH}/src
export MTIM_BIN_PATH=${MTIM_PATH}/bin
export INTERPRETER=octave
export MATLAB_BIN_PATH=
export MATLAB_MEX_PATH=
export MATLAB_INCLUDE_DIR=
export OCTAVE_BIN_PATH=${OQTANS_DEP_PATH}/octave/bin/octave
export OCTAVE_MKOCT=${OQTANS_DEP_PATH}/octave/bin/mkoctfile
export SAMTOOLS_DIR=${OQTANS_SRC_PATH}/samtools-0.1.19
export PYTHON_PATH=/usr/bin/python${OQTANS_PYTHON_VERSION}
export PYTHONPATH=${OQTANS_DEP_PATH}/lib/python${OQTANS_PYTHON_VERSION}/site-packages:${OQTANS_DEP_PATH}/lib64/python${OQTANS_PYTHON_VERSION}/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=${OQTANS_DEP_PATH}/lib/:$LD_LIBRARY_PATH
