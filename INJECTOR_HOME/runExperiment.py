#!/usr/bin/python
import sys
import os
import argparse
import random


parser = argparse.ArgumentParser(description="Run a Sloth Experiment")
parser.add_argument('-i', '--injection_mode'
                    , help="Injection Mode: in_vivo (defaults to in_vivo)"
                    , dest='injection_mode'
                    , default = 'in_vivo')

parser.add_argument('-n', '--nb_peers'
                    , help="Number of Peers"                    
                    , dest='nb_peers'
                    , type=int
                    , required=True)

parser.add_argument('-f', '--nodes_address_file'
                    , help="Absolute pathname to the file indicating the peer addresses"
                    , dest='nodes_address_file'
                    , required=True)

parser.add_argument('-s', '--service_node'
                    , help='Name of the node where the injector will be executed'
                    , dest='service_node'
                    , required=True)

parser.add_argument('-d', '--duration'
                    , help='Duration of the simulation, in seconds (defaults to 60)'
                    , dest='duration'
                    , default=60
                    , type=int)

parser.add_argument('-o', '--nb_objects'
                    , help='Number of objects to populate the DHT in the initialization phase (defaults to 1024)'
                    , dest='nb_objects'
                    , default=1024
                    , type=int)

parser.add_argument('-x', '--object_max_size'
                    , help='Maximum size for an object, in KBs (defaults to 1024)'
                    , dest='object_max_size'
                    , default=1024
                    , type=int)

parser.add_argument('-g', '--get-period'
                    , help='The period for a GET event ocurrence, in seconds. Use 0 for no such events (defaults to 180)'
                    , dest='get_period'
                    , default=180
                    , type=int)

parser.add_argument('-p', '--put-period'
                    , help='The period for a PUT event ocurrence, in seconds. Use 0 for no such events (defaults to 180)'
                    , dest='put_period'
                    , default=180
                    , type=int)

parser.add_argument('-c', '--crash-period'
                    , help='The period for a CRASH event ocurrence, in seconds. Use 0 for no such events (defaults to 600)'
                    , dest='crash_period'
                    , default=600
                    , type=int)

parser.add_argument('-w', '--crash-duration'
                    , help='The duration of a crash, in seconds (defaults to 600)'
                    , dest='crash_duration'
                    , default=600
                    , type=int)

parser.add_argument('-r', '--removal-period'
                    , help='The period for a DROP event ocurrence, in seconds. Use 0 for no such events (defaults to 300)'
                    , dest='removal_period'
                    , default=300
                    , type=int)

parser.add_argument('-u', '--removal-duration'
                    , help='The duration of a voluntary removal, in seconds (defaults to 300)'
                    , dest='removal_duration'
                    , default=300
                    , type=int)
                    

def main():
    args = parser.parse_args()
    cmd = './runExperiment.sh %s %d %s %s' % (args.injection_mode, args.nb_peers, args.nodes_address_file, args.service_node)
    os.system(cmd)
   
if __name__ == '__main__':
    try:
       os.environ["SLOTH_HOME"]
       os.environ["INJECTOR_HOME"]
    except KeyError:
       sys.exit("Please set the SLOTH_HOME and INJECTOR_HOME env variables")
    main()
    
                

	
