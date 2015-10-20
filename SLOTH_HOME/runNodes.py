#!/usr/bin/python
import sys
import os
import subprocess
import time
import argparse
import hashlib
from execo import TaktukRemote, TaktukPut, logger, Host
from execo.substitutions import remote_substitute

parser = argparse.ArgumentParser(description="Run Sloth DHT Nodes")
parser.add_argument('nbNodes', type=int, metavar="N", help="Number of nodes")
parser.add_argument('dataMode', metavar="M", help="Data Mode = eager | lazy")
parser.add_argument('--experimentId', type=int, metavar="E",
                    help="Experiment id (default = 0)",
                    default=0, required=False)
parser.add_argument('--no-stabilization',
                    help="Turns off periodic stabilization",
                    required=False,
                    action='store_true')
parser.add_argument('--nodes_address_file',
                    help="Absolute pathname to the file indicating the peer addresses",
                    required=True,
                    metavar="F",
                    default="./configuration/nodes_address.txt")

def main():

    args = parser.parse_args()
    otherFlags = "--known-peers-file " + args.nodes_address_file
    if args.no_stabilization:
        otherFlags += " --no-stabilization"

    login = str(os.getlogin())
    logger.info("Running Experiment: %d with user %s" %(args.experimentId, login))

    # Retrieve the right number of lines
    try:
        nodesFile = open(args.nodes_address_file)
        nodesInfos = [next(nodesFile) for x in range(args.nbNodes)]
        nodesFile.close()
    except IOError as e:
        logger.error("I/O error({0}) on " + args.nodes_address_file + \
            ": {1}".format(e.errno, e.strerror))
        sys.exit(1)
     
    if len(nodesInfos) != args.nbNodes:
        logger.error("There is no enough addresses in the file")
        sys.exit(1)

    hosts = [s.strip().split(':')[0] for s in nodesInfos]
    akkaports = [s.strip().split(':')[1] for s in nodesInfos]
    httpports = [s.strip().split(':')[2] for s in nodesInfos]
    flags = ['-fd'] * args.nbNodes
     
    #@ Build delay according to the peer ID 
    logger.info("Constructing hashes of peer ids")
    hp_shas = [((h+':'+p), int(hashlib.sha1(h+':'+p).hexdigest(),16)) for (h,p) in zip(hosts, akkaports)]
    hp_shas.sort(key=lambda t: t[1]) 

    logger.info("Creating sorted peers list and corresponding delays")    
    sorted_peers = [h for (h,sha) in hp_shas ]
    delays = [sorted_peers.index(h+':'+p)*.5 for (h,p) in zip(hosts, akkaports)]

    logger.info("Setting -ifd flags for initial peer")
    index = delays.index(0)
    flags[index]='-ifd'
   
    ## Overwrite the nodes address file
    logger.info("Overwriting nodes address file, now with sorted peers")
    nodesFile = open(args.nodes_address_file, 'w')
    nhosts = [s.strip().split(':')[0] for s in sorted_peers]
    nakkaports  = [s.strip().split(':')[1] for s in sorted_peers]
    for (h,p) in zip(nhosts,nakkaports): 
        nodesFile.write("%s:%s:%d\n" % (h,p,int(p)+5000))
    nodesFile.close()    
    
    logger.info("Initial peer: %s:%s with flags %s" % (hosts[index],httpports[index],flags[index]))
 
    # Copy the known address file 
    filtered_hosts = list(set(hosts))
    logger.info("Putting addresses file %s into hosts %s" % (args.nodes_address_file, filtered_hosts)) 
    cp = TaktukPut(filtered_hosts, [str(args.nodes_address_file)],
                   remote_location=str(args.nodes_address_file)).run()

    rm_tmp_cmd = '; '.join([
        ## 'rm -rf /tmp/sloth'
        ## , 'mkdir -p /tmp/sloth/%d' % args.experimentId
        'mkdir -p /tmp/sloth/%d' % args.experimentId
    ])

    logger.info("Recreating /tmp/sloth/%d folder on hosts %s" % (args.experimentId, filtered_hosts))
    TaktukRemote(rm_tmp_cmd, filtered_hosts, connection_params={'user':login}).run()

    startNodeCmd = ' '.join([
        './startNode.sh ' + args.dataMode + ' {{akkaports}}'
        , str(args.experimentId) + ' --mode ' + args.dataMode
        , '--port {{akkaports}}'
        , '--http-port {{httpports}} {{flags}} ' + otherFlags
        , '2>&1 > /tmp/sloth/'+str(args.experimentId)+'/sloth_launcher_{{akkaports}}_' + args.dataMode + '.log 0<&- 2>&- &'
    ])

    cmd = '; '.join([      
        'cd ~/SLOTH-EXP-TMP/SLOTH_HOME'
        , 'sleep {{delays}}'
        , startNodeCmd
    ])

    logger.info("Launching peers with command: %s" % cmd)

    remoteCmdsFile = open("remote_cmds_%d.info" % args.experimentId, 'w')
    logger.info("Writing peer-specific commands into %s" % remoteCmdsFile)
    for h in hosts:
        remoteCmdsFile.write(remote_substitute(cmd, [Host(h) for h in hosts], hosts.index(h), (globals(), locals())))
        remoteCmdsFile.write("\n")
    remoteCmdsFile.close()

    logger.info("Launching peers... this may take a while ...")
    launch_sloths = TaktukRemote(cmd, hosts, connection_params={'user': login}).run()
    
    p_nb=0; 
    for peer in launch_sloths.processes: 
        if not peer.ok:
            logger.error(peer.host)
            logger.error(peer.stdout)
            logger.error(peer.stderr)
        else: 
            p_nb= p_nb + 1

    logger.info("%d Peers have been launched" % (p_nb))
    if p_nb != args.nbNodes:
        logger.error("Unfortunately you requested %d peers, so bye bye (you can try to relaunch it with %d peers, it can run ...)" % (args.nbNodes, p_nb))
        sys.exit(1)


if __name__ == "__main__":
    main()
