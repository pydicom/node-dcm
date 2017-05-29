#!/bin/sh

# Use provided getcookies.py to download datasets
SCRIPT=`realpath -s $0`
HERE=`dirname $SCRIPT`
python $HERE/getcookies.py --output /data
