#!/bin/bash

./copyFiles.sh

git add .
git commit -m "New release of Sloth / Injector"
git push

rsync -avrzd -e ssh --progress --exclude-from rsync-exclude . g5k:lyon/DHT-EXP




