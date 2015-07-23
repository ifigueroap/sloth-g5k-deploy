#!/bin/bash

: ${SLOTH_HOME?"The SLOTH_HOME environment variable should be set (please proceed: export SLOTH_HOME=...)"}
: ${INJECTOR_HOME?"The INJECTOR_HOME environment variable should be set (please proceed: export INJECTOR_HOME=...)"}

if [ $# -ne 4 ]; then 
	echo "Usage: ./runExperiment.sh INJECTION_MODE NBNODE NODEFILE SERVICENODE"
	exit
fi

EXPERIMENTID=$RANDOM
echo "Experiment with Id: " $EXPERIMENTID

INJECTION_MODE=$1
NBNODE=$2
ORIG_NODEFILE=$3 
SERVICENODE=$4

function executeExperiment {
    MODE=$1
    echo "Starting ${MODE} Experiment"

    NODEFILE=/tmp/$(whoami)-$( basename $ORIG_NODEFILE)
    head -n $((NBNODE)) $ORIG_NODEFILE > $NODEFILE
    # TODO check number of lines
    echo "Number of peers available $(wc -l $NODEFILE) (requested: $NBNODE)"

    echo "  Check and kill previous peers"
    sync
    cd $SLOTH_HOME
    ./killNodes.py --nodes_address_file $NODEFILE
    
   echo "  Launch ${NBNODE} new peers"
    cd $SLOTH_HOME
    if [ "$INJECTION_MODE" != "in_vivo" ]; then 
       echo "./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID --no-stabilization"
       echo $PWD
       ./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID --no-stabilization
    else
       echo "./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID"
       echo $PWD
       ./runNodes.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID
    fi
    
  
    if [ $? -ne 0 ] ; then
       exit 1 
    fi
 
    echo "  Please wait 20 seconds that the ring becomes more stabilized"
    sleep 20 
   
    echo "  Start the injection phase (with user: $USER)"
    cd $INJECTOR_HOME
    ./runInjector.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID  --service_node $SERVICENODE --user $USER 

 
    #    echo "Killing peers"
#    cd $SLOTH_HOME
#    ./killNodes.py --nodes_address_file $NODEFILE
}

echo "Executing Eager Experiment"
executeExperiment eager 

#echo "Executing Lazy Experiment"
#executeExperiment lazy

# echo "Processing logs and creating ECDF plots"
# #Process logs and create ECDF plots
# cd $SLOTH_HOME
# Rscript ecdfCLI.R $EXPERIMENTID

echo "Done!"

