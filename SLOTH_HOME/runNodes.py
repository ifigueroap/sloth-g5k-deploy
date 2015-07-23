#!/usr/bin/python
import sys
import os
import subprocess
import time
import argparse
import hashlib
from execo import TaktukRemote, TaktukPut

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

    otherFlags = "--known-nodes-file " + args.nodes_address_file
    if args.no_stabilization:
        otherFlags += " --no-stabilization"

    login = str(os.getlogin())

    # Retrieve the right number of lines
    try:
        nodesFile = open(args.nodes_address_file)
        nodesInfos = [next(nodesFile) for x in range(args.nbNodes)]
        nodesFile.close()
    except IOError as e:
        print "I/O error({0}) on " + args.nodes_address_file + \
            ": {1}".format(e.errno, e.strerror)
        sys.exit(1)
     
    if len(nodesInfos) != args.nbNodes:
        print "There is no enough addresses in the file"
        sys.exit(1)

    hosts = [s.strip().split(':')[0] for s in nodesInfos]
    akkaports = [s.strip().split(':')[1] for s in nodesInfos]
    httpports = [s.strip().split(':')[2] for s in nodesInfos]
    flags = ['-fd'] * args.nbNodes
    delays = [float(x) / 10 for x in range(0, args.nbNodes * 7, 7)]
     
    #@ Build delay according to the peer ID 
    hp_shas = [((h+':'+p), int(hashlib.sha1(h+':'+p).hexdigest(),16)) for (h,p) in zip(hosts, akkaports)]
    hp_shas.sort(key=lambda t: t[1])
    print ([str(hp_sha) + '\n' for hp_sha in hp_shas])
 
    sorted_peers = [h for (h,sha) in hp_shas ]
    #positions = [sorted_peers.index(h+':'+p) for (h,p) in zip(hosts, akkaports)]
    #print positions
    delays = [sorted_peers.index(h+':'+p)*.5 for (h,p) in zip(hosts, akkaports)]
    print delays
    index = delays.index(0)
    print str(index) + ':'+str(len(flags))+':'+str(len(delays))
    flags[index]='-ifd'
   
    ## Overwrite the nodes address file
    nodesFile = open(args.nodes_address_file, 'w')
    nhosts = [s.strip().split(':')[0] for s in sorted_peers]
    nakkaports  = [s.strip().split(':')[1] for s in sorted_peers]
    for (h,p) in zip(nhosts,nakkaports): 
        nodesFile.write("%s:%s:%d\n" % (h,p,int(p)+5000))
    nodesFile.close()
    
    
    print "%s %s %s file:%s "%(hosts[index],httpports[index],flags[index],args.nodes_address_file)

    #print hosts
    #print akkaports
    #print httpports
    #print flags

    # Copy the known address file 
    filtered_hosts = list(set(hosts))
    print 'copy %s on %s' % (args.nodes_address_file, filtered_hosts)

    cp = TaktukPut(filtered_hosts, [str(args.nodes_address_file)],
                   remote_location=str(args.nodes_address_file)).run()

    cmd = 'rm -rf /tmp/sloth ; mkdir -p /tmp/sloth/' + str(args.experimentId) \
        + ' ; cd ~/SLOTH-EXP-TMP/SLOTH_HOME; sleep {{delays}} ; ' + \
        './startNode.sh ' + args.dataMode + ' {{akkaports}} ' + \
        str(args.experimentId) + ' --mode ' + args.dataMode + \
        ' --port {{akkaports}} ' +\
        '--http-port {{httpports}} {{flags}} ' + otherFlags + \
        ' 2>&1 > /tmp/sloth/' + str(args.experimentId) + \
        '/sloth_launcher_{{akkaports}}_' + args.dataMode + '.log 0<&- 2>&- &'
    print cmd + ':' + login
    launch_sloths = TaktukRemote(cmd, hosts,
                                 connection_params={'user': login}).run()
    
    p_nb=0; 
    for peer in launch_sloths.processes: 
        if not peer.ok:
            print peer.host
            print peer.stdout
            print peer.stderr
        else: 
            p_nb= p_nb + 1

    print "%d Peers have been launched" % (p_nb)
    if p_nb != args.nbNodes:
        print "Unfortunately you requested %d peers, so bye bye (you can try to relaunch it with %d peers, it can run ...)" % (args.nbNodes, p_nb)
        sys.exit(1)


if __name__ == "__main__":
    main()
