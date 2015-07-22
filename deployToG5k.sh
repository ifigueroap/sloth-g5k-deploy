#!/bin/bash

THISDIR=$PWD

echo "### sbt assembly SLOTH ###"
cd $SLOTH_HOME_DEV
sbt assembly

echo "### sbt assembly INJECTOR ###"
cd $INJECTOR_HOME_DEV
sbt assembly

echo "Copying files..."
cd $THISDIR
./copyFiles.sh

echo "Adding to git..."
git add .
git commit -m "New release of Sloth / Injector"
git push

echo "Done!"



