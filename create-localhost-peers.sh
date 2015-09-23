#!/bin/bash

rm -f peers.list
for ((i=0; i<$1; i++)); do echo `hostname`:$((i+3000)):$((i+8000)) >> peers.info; done;

