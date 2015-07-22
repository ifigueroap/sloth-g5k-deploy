#!/usr/bin/env python
from execo import TaktukRemote, TaktukPut, default_connection_params, logger, Process
from execo_g5k import *
import os, sys, argparse
from time import sleep 


parser = argparse.ArgumentParser(description="Configure the nodes with all mandatory files")
parser.add_argument('-f', '--nodes_address_file', dest="nodes_address_file", help="file containting node addresses", required=True)
parser.add_argument('-s', '--service_node', dest="service_node", help="name of the node where the injector will be executed", required=True)

def main():
    args = parser.parse_args()
 
    # Retrieve the right number of lines
    try:
        nodesFile = open(args.nodes_address_file)
        nodesInfos = [line for line in nodesFile]
    except IOError as e:
       print "I/O error({0}) on "+args.nodes_address_file+": {1}".format(e.errno, e.strerror)
       sys.exit()
    
    hosts  = [s.strip().split(':')[0] for s in nodesInfos]
    hosts.append(args.service_node)
    frontends = list(set([str('frontend.'+get_host_site(h)) for h in hosts]))
    

    ## Remove the old DHT-EXP hierarchy 
    logger.info('Remove old files on each NFS server involved in the experiment ('+str(frontends)+')')
    whoami=os.getlogin()
    cmd = 'rm -rf ~/SLOTH-EXP-TMP' 
    TaktukRemote(cmd, frontends, connection_params={'user': str(whoami)}).run()


    ## Copy the DHT-EXP hierarchy to the remote site
    logger.info('Copy sloth and injector files on each NFS server involved in the experiment ('+str(frontends)+')')
    TaktukRemote('mkdir ~/SLOTH-EXP-TMP/', frontends, connection_params={'user': str(whoami)}).run()
    TaktukPut(frontends, ['SLOTH_HOME'],'/home/'+str(os.getlogin())+'/SLOTH-EXP-TMP/.', connection_params={'user': str(whoami)}).run()
    TaktukPut(frontends, ['INJECTOR_HOME'],'/home/'+str(os.getlogin())+'/SLOTH-EXP-TMP/.', connection_params={'user': str(whoami)}).run()


    test = TaktukPut(frontends, ['' ], connection_params={'user': str(whoami)}).run()
 
if __name__ == "__main__":
    main()
