#!/usr/bin/env python
from execo import TaktukRemote, TaktukPut, default_connection_params, logger, Process, Put
from execo_g5k import *
import os, sys, argparse
from time import sleep 
from execo.log import style
from execo_g5k import get_oargrid_job_oar_jobs
from execo_engine.utils import copy_outputs


parser = argparse.ArgumentParser(description="Configure the nodes with all mandatory files")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-j', '--job_ids', nargs='+',  help="oar job id - site:jobid site:jobid ...)")
group.add_argument('-g', '--grid_job_id', nargs=1, help="grid job id")


def main():
    copy_outputs('config.log', 'config.log')
    args = parser.parse_args()
    whoami = os.getlogin()
    logger.info('whoami: %s', whoami)   
    
    jobids = []
    if args.grid_job_id == None:
        jobids = args.job_ids
    else:
        grid_job_id = int(args.grid_job_id[0])
        jobids = ["%s:%d" % (site, job_id) for job_id, site in get_oargrid_job_oar_jobs(grid_job_id)]

    logger.info('Using jobs %s', style.emph(' '.join(jobids)))
    
    sites  = [j.strip().split(':')[0] for j in jobids]
    frontends = [str('frontend.'+s) for s in sites]
    oar_ids  = [j.strip().split(':')[1] for j in jobids]
    
    jobids_list=[(int(j.strip().split(':')[1]),str(j.strip().split(':')[0])) for j in jobids]
#    print sites
#    print oar_ids
#    print jobids_list 
#    print frontends

    logger.info("Get list of associated nodes")
    nodes = [ job_nodes for job in jobids_list for job_nodes in get_oar_job_nodes(*job) ]
 #   logger.info('%s', hosts_list(nodes))
    logger.info('%s', nodes)
 
    logger.info("Deploying %i nodes" % (len(nodes),))
    deployed, undeployed = deploy(Deployment(nodes, env_name = "jessie-x64-nfs"))
    logger.info("%i deployed, %i undeployed" % (len(deployed), len(undeployed)))
 
    ## Configure Host OSes
    logger.info('Finalize node customization')
    # use root to connect on the host
    default_connection_params['user'] = 'root'

    ## Copy local .ssh to remote nodes: 
    logger.info('Copy ssh entries into root of each node')
    Put(nodes, ['/home/'+whoami+'/.ssh/id_rsa','/home/'+whoami+'/.ssh/id_rsa.pub'],'.ssh/.').run()

    ## Install missing packages
    logger.info('| - Install Packages')   
    install_packages = TaktukRemote('export DEBIAN_MASTER=noninteractive ; export https_proxy="https://proxy:3128"; apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --force-yes python-pip lynx openjdk-8-jdk uuid-runtime cpufrequtils kanif -o Acquire::Check-Valid-Until=false -o Dpkgtions::="--force-confdef" -o Dpkgtions::="--force-confold" ; pip install tabview', nodes).run()
    ## Fix ulimit and related stuffs
    logger.info('| - set limit related stuffs')
    cmd = 'ulimit -c unlimited; sysctl -w vm.max_map_count=331072 ; echo 120000 > /proc/sys/kernel/threads-max ; echo 600000 > /proc/sys/vm/max_map_count ; echo 200000 > /proc/sys/kernel/pid_max' 
    TaktukRemote(cmd, nodes).run()

    ## Copy the DHT-EXP hierarchy to the remote site
    logger.info('Copy sloth and injector files on each NFS server involved in the experiment')
    TaktukRemote('mkdir -p ~/SLOTH-EXP-TMP/', frontends, connection_params={'user': str(whoami)}).run()
    TaktukPut(frontends, ['./SLOTH_HOME' ],'./SLOTH-EXP-TMP/.', connection_params={'user': str(whoami)}).run()
    TaktukPut(frontends, ['./INJECTOR_HOME' ], './SLOTH-EXP-TMP/.', connection_params={'user': str(whoami)}).run()


    ## Prepare the address file for the sloth peers (please remind that the last node is dedicated for the injector
    logger.info('Prepare the peers list')
    
    f1 = open('./hosts.info', 'w')
    f2 = open('./peers.info', 'w')

    logger.info('enumerate %s', enumerate(nodes[:-1]))

    i = 0
    for j, node in enumerate(nodes[:-1]):
        f1.write("%s\n" % (node.address))
        for cores in range(get_host_attributes(node)['architecture']['smt_size']):
            f2.write("%s:%d:%d\n" % (node.address, 3000 + i, 8000 + i))
            i = i + 1
    f1.close()
    f2.close()

    f = open('./service_node.info', 'w')
    f.write("%s" % nodes[-1].address) 
    f.close()
    
    logger.info("Nodes are now ready, you should launch ./runExperiment.sh ... from the lyon frontend")
    logger.info("The list of sloth peers is in ./peers.info")
    logger.info("The service node is in ./service_node.info")
    logger.info("The injector will run on %s" % nodes[-1].address)
    logger.info("The usual(max)  command should be : ./runExperiment.sh in_vivo %d %s/peers.info %s" % (i,os.getcwd(),nodes[-1].address))

  
 
if __name__ == "__main__":
    main()
