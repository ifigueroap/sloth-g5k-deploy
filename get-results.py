#!/usr/bin/env python
from execo import Get, TaktukRemote, TaktukGet, default_connection_params, logger, Process
from execo_g5k import *
import os, sys, argparse
from time import sleep 


parser = argparse.ArgumentParser(description="Configure the nodes with all mandatory files")
parser.add_argument('-f', '--nodes_address_file', dest="nodes_address_file", help="file containting node addresses", required=True)
parser.add_argument('-s', '--service_node', dest="service_node", help="name of the node where the injector will be executed", required=True)
parser.add_argument('-e', '--experiment_id', dest="experiment_id", help="Id of the experiement (see ./runExperiment.sh returned value", required=True)

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
    hosts_filtered=list(set(hosts))
    frontends = list(set([str('frontend.'+get_host_site(h)) for h in hosts]))

    #Create local direction
    results_path='~/DHT-EXP-RESULTS/'+str(args.experiment_id)+'/'
    os.system('mkdir -p '+results_path)

    whoami=os.getlogin()
    
    ## Get peers logs  
    logger.info('Make an archive on each node ('+str(hosts_filtered)+')')
    cmd = 'tar czf /tmp/{{{host}}}.tgz /tmp/sloth/'
    TaktukRemote(cmd, hosts_filtered, connection_params={'user': str(whoami)}).run()
    logger.info('Collect the archives')
    Get(hosts_filtered, ['/tmp/{{{host}}}.tgz'],results_path,  connection_params={'user': str(whoami)}).run()
    logger.info('Extract the archives')
    for host in hosts_filtered:
        cmd = 'tar xzf '+results_path+host+'.tgz -C '+results_path +' --strip=3'
        print cmd
        os.system(cmd)

    ## Get Injector logs 
    logger.info('get log files of the injector ('+str(args.service_node)+')')
    remote_files=['/home/'+str(whoami)+'/DHT-EXP/INJECTOR_HOME/dhtinjector-log-'+str(args.experiment_id)+'-eager.log', '/home/'+str(whoami)+'/DHT-EXP/INJECTOR_HOME/dhtinjector-log-'+str(args.experiment_id)+'-lazy.log'] 

    test = Get(str(args.service_node), remote_files, results_path, connection_params={'user': str(whoami)}).run()
 
   ## CP peers.list
    logger.info('cp peers list')
    os.system('cp '+args.nodes_address_file+' '+results_path) 
 
if __name__ == "__main__":
    try: 
        os.environ["SLOTH_HOME"]
    except KeyError: 
        sys.exit("Please set the SLOTH_HOME env variable")
    main()
