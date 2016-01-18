#!/bin/bash

: ${SLOTH_HOME?"The SLOTH_HOME environment variable should be set (please proceed: export SLOTH_HOME=...)"}
: ${INJECTOR_HOME?"The INJECTOR_HOME environment variable should be set (please proceed: export INJECTOR_HOME=...)"}

if [ $# -lt 4 ]; then 
	echo "Usage: ./runExperiment.sh MODE NBNODE NODEFILE SERVICENODE"
	exit
fi

if [ ! -d "$HOME/SLOTH-EXP-TMP" ]; then
	echo "The ~/SLOTH-EXP-TMP folder must be created before being able to run an experiment. Please create it."
        exit
fi

EXPERIMENTID=0
echo "Just running SLOTH with experimentId: 0"

MODE=$1
NBNODE=$2
ORIG_NODEFILE=$3 
SERVICENODE=$4
THEPWD=$PWD

INJECTOR_PARAMS=${@:5}

echo $INJECTOR_PARAMS


function runSloth {

    echo "Running Sloth in ${MODE} mode"
    
    NODEFILE=/tmp/$(whoami)-$( basename $ORIG_NODEFILE)
    head -n $((NBNODE)) $ORIG_NODEFILE > $NODEFILE
    
    echo "Number of peers available $(wc -l $NODEFILE) (requested: $NBNODE)"
    
    echo "  Check and kill previous peers"
    sync
    cd $SLOTH_HOME
    ./killNodes.py --nodes_address_file $NODEFILE
    
    echo "  Launch ${NBNODE} new peers"
    cd $SLOTH_HOME
    echo "./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID"
    echo $PWD
    ./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID   
  
    if [ $? -ne 0 ] ; then
	exit 1 
    fi
 
    echo "Sloth should be running now"
}

runSloth
