#!/bin/sh

#source /grid/fermiapp/minerva/setup/setup_minerva_products.sh

export SAM_EXPERIMENT=minerva
export SAMWEB_DIR=$HOME/sam-web-client
export PATH=$PATH:$SAMWEB_DIR/bin
export SAMWEB_SRC=$SAMWEB_DIR/python
export PYTHONPATH=$PYTHONPATH:$SAMWEB_DIR/python
#setup encp -q stken:x86_64