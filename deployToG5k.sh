#!/bin/bash

THISDIR=$PWD

echo "### sbt assembly SLOTH ###"
cd $SLOTH_HOME_DEV
sbt assembly 
if [$? -ne 0]; then
   exit 1
fi

echo "### sbt assembly INJECTOR ###"
cd $INJECTOR_HOME_DEV
sbt assembly
if [$? -ne 0]; then
  exit 1
fi

echo "Copying files..."
cd $THISDIR
./copyFiles.sh

echo "Adding to git..."
git add .
git commit -m "New release of Sloth / Injector"
git push

echo "Done!"



