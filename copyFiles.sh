#!/bin/bash


# -v : verbose
# -p : keep "last modified time" attribute of files. Otherwise rsync will think all files are 'new'

cp -v -p -r $SLOTH_HOME_DEV/configuration ./SLOTH_HOME
cp -v -p $SLOTH_HOME_DEV/target/sloth.jar ./SLOTH_HOME/target

cp -v -p -r $INJECTOR_HOME_DEV/config ./INJECTOR_HOME
cp -v -p $INJECTOR_HOME_DEV/target/scala-2.10/dhtinjector.jar ./INJECTOR_HOME/target/scala-2.10/
