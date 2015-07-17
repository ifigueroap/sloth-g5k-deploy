#!/bin/bash

cp -v -r $SLOTH_HOME/configuration ./SLOTH_HOME
cp -v $SLOTH_HOME/target/sloth.jar ./SLOTH_HOME/target
cp -v $SLOTH_HOME/killNodes.py $SLOTH_HOME/runNodes.py $SLOTH_HOME/startNode.sh ./SLOTH_HOME

cp -v -r $INJECTOR_HOME/config ./INJECTOR_HOME
cp -v $INJECTOR_HOME/runExperiment.sh ./INJECTOR_HOME
cp -v $INJECTOR_HOME/target/scala-2.10/dhtinjector.jar ./INJECTOR_HOME/target/scala-2.10/

git add .
git commit -m "New release of Sloth / Injector"
git push

rsync -avrzd -e ssh --progress . g5k:lyon/DHT-EXP




