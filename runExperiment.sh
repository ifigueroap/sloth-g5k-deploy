#!/bin/bash

: ${SLOTH_HOME?"The SLOTH_HOME environment variable should be set (please proceed: export SLOTH_HOME=...)"}
: ${INJECTOR_HOME?"The INJECTOR_HOME environment variable should be set (please proceed: export INJECTOR_HOME=...)"}

if [ $# -lt 4 ]; then 
	echo "Usage: ./runExperiment.sh INJECTION_MODE NBNODE NODEFILE SERVICENODE (INJECTOR_PARAMS)*"
	exit
fi

if [ ! -d "$HOME/SLOTH-EXP-TMP" ]; then
	echo "The ~/SLOTH-EXP-TMP folder must be created before being able to run an experiment. Please create it."
        exit
fi

EXPERIMENTID=$RANDOM
echo "Experiment with Id: " $EXPERIMENTID

INJECTION_MODE=$1
NBNODE=$2
ORIG_NODEFILE=$3 
SERVICENODE=$4
THEPWD=$PWD

INJECTOR_PARAMS=${@:5}

echo $INJECTOR_PARAMS


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
 
    # w=20 
    # echo "  Please wait $w seconds that the ring becomes more stabilized"
    # sleep $w 
   
    echo "  Start the injection phase (with user: $USER)"
    cd $INJECTOR_HOME
    ./runInjector.py $NBNODE $MODE --nodes_address_file $NODEFILE --experimentId $EXPERIMENTID  --service_node $SERVICENODE --user $USER $INJECTOR_PARAMS

}

echo "Executing Eager Experiment"
executeExperiment eager 

echo "Executing Lazy Experiment"
executeExperiment lazy

echo "Collecting results"
echo "./get-results.py -f $NODEFILE -s $SERVICENODE -e $EXPERIMENTID"
cd $THEPWD
./get-results.py -f $NODEFILE -s $SERVICENODE -e $EXPERIMENTID

echo "Consolidating analytics logs"
echo "cat ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/eager/analytics-* > ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/eager/analytics.log"
cat ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/eager/analytics-* > ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/eager/analytics.log

echo "cat ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/lazy/analytics-* > ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/lazy/analytics.log"
cat ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/lazy/analytics-* > ~/SLOTH-EXP-RESULTS/$EXPERIMENTID/lazy/analytics.log

# echo "Processing logs and creating ECDF plots"
# #Process logs and create ECDF plots
# cd $SLOTH_HOME
echo "Computing ECDFs"
echo "Rscript ecdfCLI.r $EXPERIMENTID"
Rscript ecdfCLI.R $EXPERIMENTID

echo "Done!"

