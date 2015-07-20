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
    frontends = list(set([str('frontend.'+get_host_site(h)) for h in hosts]))

    #Create local direction
    os.system('mkdir '+str(args.experiment_id))

    whoami=os.getlogin()
    
    ## Get peers logs  
    remote_files=['/home/'+str(whoami)+'/DHT-EXP/SLOTH_HOME/log/'+args.experiment_id+'/eager','/home/'+str(whoami)+'/DHT-EXP/SLOTH_HOME/log/'+args.experiment_id+'/lazy']
    logger.info('get log files from each NFS server involved in the experiment (frontends:'+str(frontends)+', log files:'+str(remote_files)+')')
    test = Get(frontends, remote_files, os.getcwd()+'/'+str(args.experiment_id)+'/.' ,connection_params={'user': str(whoami)}).run()

    ## Get tmp logs
    # Please note that taktukGet does not allow us to use '*' characters. 
    # Get provides such a feature but Get is not scalable enough (i.e. cannot go beyond 250 peers)
    # When will we reach such a scale, we will have to use a local tar and scp to lyon (see commented line below) 
    remote_files=['/tmp/sloth_launcher']
    logger.info('get log files from each host (i.e. tmp files)')
    test = Get(hosts, remote_files, os.getcwd()+'/'+str(args.experiment_id)+'/.' ,connection_params={'user': str(whoami)}).run()
    #cmd = 'tar czf tmp_{{{host}}}.log /tmp/sloth_launcher* ; scp /tmp_{{{host}}}.log frontend.lyon:./DHT-EXP/'+str(arg.experiment_id)+'/.'
    
    ## Get Injector logs 
    logger.info('get log files of the injector ('+str(args.service_node)+')')
    remote_files=[''/home/'+str(whoami)+'/DHT-EXP/INJECTOR_HOME/dhtinjector-log-'+str(args.experiment_id)+'_eager.log', /home/'+str(whoami)+'/DHT-EXP/INJECTOR_HOME/dhtinjector-log-'+str(args.experiment_id)+'_lazy.log'], 

    test = TaktukGet(str(args.service_node), remote_files, os.getcwd()+'/'+str(args.experiment_id)+'/.', connection_params={'user': str(whoami)}).run()
    ## CP peers.list
    logger.info('cp peers list')
    os.system('cp '+args.nodes_address_file+' ./'+args.experiment_id+'/.') 
 
if __name__ == "__main__":
    try: 
        os.environ["SLOTH_HOME"]
    except KeyError: 
        sys.exit("Please set the SLOTH_HOME env variable")
    main()
