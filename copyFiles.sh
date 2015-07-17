#!/bin/bash


# -v : verbose
# -p : keep "last modified time" attribute of files. Otherwise rsync will think all files are 'new'

cp -v -p -r $SLOTH_HOME/configuration ./SLOTH_HOME
cp -v -p $SLOTH_HOME/target/sloth.jar ./SLOTH_HOME/target

cp -v -p -r $INJECTOR_HOME/config ./INJECTOR_HOME
cp -v -p $INJECTOR_HOME/target/scala-2.10/dhtinjector.jar ./INJECTOR_HOME/target/scala-2.10/
