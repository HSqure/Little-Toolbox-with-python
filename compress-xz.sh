#!/bin/bash

# USAGE: 
# compress-xz.sh <FILENAME>

TRD_NUM=0 # set 0 to allow maximoum cpu treads number
COMPRESS_GRADE=9 # 1-9

tar -cvf - ${1} | xz -9T 0 - > ${1}.tar.xz
