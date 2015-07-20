#!/usr/bin/python
import sys
import os
import subprocess
import time
import argparse
from execo import TaktukRemote, TaktukPut

parser = argparse.ArgumentParser(description="Run the Sloth Injector")
parser.add_argument('nbNodes', type=int, metavar="N", help="Number of nodes")
parser.add_argument('dataMode', metavar="M", help="Data Mode = eager | lazy")
parser.add_argument('--experimentId', type=int, metavar="E", help="Experiment id (default = 0)", default = 0, required=False)
parser.add_argument('--nodes_address_file', help="Absolute pathname to the file indicating the peer addresses", required=True, metavar="F", default = "./configuration/nodes_address.txt")
parser.add_argument('-s', '--service_node', help="name of the node where the injector will be executed", required=True)

def main():

    args = parser.parse_args()

    # Retrieve the right number of lines
    try:
        nodesFile = open(args.nodes_address_file)
        nodesInfos = [next(nodesFile) for x in range(args.nbNodes)]
    except IOError as e:
       print "I/O error({0}) on "+args.nodes_address_file+": {1}".format(e.errno, e.strerror)
       sys.exit()
   
    if len(nodesInfos) < int(args.nbNodes):
        print "There is no enough addresses in the file (%d requested/%d available)" % (args.nbNodes, len(nodesInfos))
        sys.exit()
    
    hosts  = [s.strip().split(':')[0] for s in nodesInfos]
    
    service_node = str(args.service_node)
    
    cp = TaktukPut(service_node, [str(args.nodes_address_file)], remote_location=str(args.nodes_address_file)).run()
    
    cmd = 'pkill -9 -f dhtinjector.jar ; rm -rf ~/DHT-EXP/INJECTOR_HOME/dhtinjector-log-*'
    launch_sloths = TaktukRemote(cmd,service_node, connection_params={'user': str(os.getlogin())}).run()

    cmd = 'cd '+os.environ["INJECTOR_HOME"]+';'\
    'cp ./config/injector.properties ./config/injector.properties.orig;'\
    'sed "s/peers.number.*/peers.number ='+str(args.nbNodes)+'/g" ./config/injector.properties > /tmp/injector.properties;'\
    'cp /tmp/injector.properties ./config/injector.properties;'\
    'sed "s/injection.mode.*/injection.mode = in_vivo/g" ./config/injector.properties > /tmp/injector.properties;'\
    'cp /tmp/injector.properties ./config/injector.properties;'\
    'sed "s:dht.nodesaddress.*:dht.nodesaddress = "'+args.nodes_address_file+'":g" ./config/injector.properties > /tmp/injector.properties;'\
    'cp /tmp/injector.properties ./config/injector.properties;'\
    'java -jar target/scala-2.10/dhtinjector.jar 2>&1 > ./dhtinjector-log-'+str(args.experimentId)+'-'+str(args.dataMode)+'.log 0<&- 2>&-'
    print service_node +'/'+ cmd
    
    launch_sloths = TaktukRemote(cmd,service_node, connection_params={'user': str(os.getlogin())}).run()
    print "The injector has been launched." 

if __name__ == "__main__":
    try: 
        os.environ["INJECTOR_HOME"]
    except KeyError: 
        sys.exit("Please set the INJECTOR_HOME env variable")
    main()
