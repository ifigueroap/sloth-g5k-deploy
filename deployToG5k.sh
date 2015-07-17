#!/bin/bash

cp -r $SLOTH_HOME/configuration .
cp $SLOTH_HOME/target/sloth.jar ./SLOTH_HOME/target
cp $SLOTH_HOME/killNodes.py $SLOTH_HOME/runNodes.py $SLOTH_HOME/startNode.sh ./SLOTH_HOME

cp -r $INJECTOR_HOME/config ./INJECTOR_HOME
cp $INJECTOR_HOME/runExperiment.sh ./INJECTOR_HOME
cp $INJECTOR_HOME/target/scala-2.10/dhtinjector.jar ./INJECTOR_HOME/target/scala-2.10/
