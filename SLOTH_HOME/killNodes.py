#!/usr/bin/env python
import sys
import os
import subprocess
import argparse
from execo import TaktukRemote, TaktukPut, default_connection_params, logger, Process


parser = argparse.ArgumentParser(description="Kill Sloth DHT Nodes")
parser.add_argument('-f', '--nodes_address_file', dest='nodes_address_file', help="Absolute pathname to the file indicating the peer addresses", required=True, metavar="F", default = "./config/nodes_address.txt")


args = parser.parse_args()

# retrieve the list of hosts from the file
# retrieve the list of hosts from the file
hosts = list(set([line.strip().split(':')[0] for line in open(args.nodes_address_file)]))
filtered_hosts=list(set(hosts))
filtered_hosts.sort()
print "Killing hosts" + str(filtered_hosts)
logger.info('kill java sloth peers')
TaktukRemote('pkill -9 -f sloth.jar ', filtered_hosts).run()

