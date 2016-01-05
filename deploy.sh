#!/bin/bash

THISDIR=$PWD

echo "### sbt assembly SLOTH ###"
cd $SLOTH_HOME_DEV
sbt assembly 
if [ $? -ne 0 ]; then
   exit 1
fi

echo "### sbt assembly INJECTOR ###"
cd $INJECTOR_HOME_DEV
sbt assembly
if [ $? -ne 0 ]; then
  exit 1
fi

echo "Copying files..."
cd $THISDIR
# -v : verbose
# -p : keep "last modified time" attribute of files. Otherwise rsync will think all files are 'new'

cp -v -p -r $SLOTH_HOME_DEV/configuration ./SLOTH_HOME
cp -v -p $SLOTH_HOME_DEV/target/sloth.jar ./SLOTH_HOME/target

cp -v -p -r $INJECTOR_HOME_DEV/config ./INJECTOR_HOME
cp -v -p $INJECTOR_HOME_DEV/target/scala-2.10/dhtinjector.jar ./INJECTOR_HOME/target/scala-2.10/


read -p "Push to github? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
   # do dangerous stuff
   echo "Adding to git..."
   git add . --all
   git commit -m "New release of Sloth / Injector"
   git push
fi

if [ $? -ne 0 ]; then
  exit 1
fi

echo "Done!"

