#!/bin/bash
#: ${SLOTH_HOME?"The SLOTH_HOME environment variable should be set (please proceed: export SLOTH_HOME=...)"}

#if [ -z "$SLOTH_HOME" ]; then 
#    echo "The SLOTH_HOME environment variable is unset (please export SLOTH_HOME=..."
#    exit 1 
#fi 



# run node with given port and http-port
echo "java -DSlothMode=$1 -DpeerPort="$2" -DExperimentId="$3" -jar ./target/sloth.jar ${*:4}"
 
java -DSlothMode=$1 -DpeerPort="$2" -DExperimentId="$3" -jar ./target/sloth.jar ${*:4} 
if [ $? -eq 0 ]; then
    echo "The chord peer has not been correctly started, please see the log"
fi
