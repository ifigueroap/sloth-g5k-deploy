#!/bin/bash

EXPERIMENTID=$1

echo "Creating folder $EXPERIMENTID/eager and $EXPERIMENTID/lazy..."
mkdir -p $EXPERIMENTID/eager
mkdir -p $EXPERIMENTID/lazy

echo "Fetching analytics logs from g5k:/lyon/DHT-EXP/$EXPERIMENTID..."

scp -r g5k:lyon/DHT-EXP/$EXPERIMENTID/eager/analytics* ./$EXPERIMENTID/eager/
scp -r g5k:lyon/DHT-EXP/$EXPERIMENTID/lazy/analytics* ./$EXPERIMENTID/lazy/

function consolidateLogs {
   cat $LOGPATH/analytics-node-* | sort -k1 > $LOGPATH/analytics.log
#   cat $LOGPATH/node-* | sort -k1 > $LOGPATH/app.log
}

echo "Consolidating analytics log files for EAGER..."
LOGPATH=./$EXPERIMENTID/eager
consolidateLogs

echo "Consolidating analytics log files for LAZY..."
LOGPATH=./$EXPERIMENTID/lazy
consolidateLogs

echo "Generating plots..."
Rscript ecdfCLI.R $EXPERIMENTID

