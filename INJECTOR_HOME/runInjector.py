#!/usr/bin/python
import sys
import os
import subprocess
import time
import argparse
from execo import Remote, TaktukPut, logger

parser = argparse.ArgumentParser(description="Run the Sloth Injector")
parser.add_argument('nbNodes', type=int, metavar="N", help="Number of nodes")
parser.add_argument('dataMode', metavar="M", help="Data Mode = eager | lazy")
parser.add_argument('--experimentId', type=int, metavar="E", help="Experiment id (default = 0)", default = 0, required=False)
parser.add_argument('--nodes_address_file', help="Absolute pathname to the file indicating the peer addresses", required=True, metavar="F", default = "./configuration/nodes_address.txt")
parser.add_argument('-s', '--service_node', help="name of the node where the injector will be executed", required=True)
parser.add_argument('-u', '--user', help="login of the user launching the script")

def main():

    args = parser.parse_args()

    login=''
    try: 
        login=os.getlogin()
    except OSError:
        login=args.user
    ## TODO make it more robust, if arg.user is empty  


   # Retrieve the right number of lines
    try:
        nodesFile = open(args.nodes_address_file)
        nodesInfos = [next(nodesFile) for x in range(args.nbNodes)]
    except IOError as e:
       logger.error("I/O error({0}) on "+args.nodes_address_file+": {1}".format(e.errno, e.strerror))
       sys.exit()
   
    if len(nodesInfos) < int(args.nbNodes):
        logger.error("There is no enough addresses in the file (%d requested/%d available)" % (args.nbNodes, len(nodesInfos)))
        sys.exit()
    
    hosts  = [s.strip().split(':')[0] for s in nodesInfos]
    
    service_node = str(args.service_node)
    
    logger.info("Killing injector processes in service node %s" % service_node)
    cmd = 'pkill -9 -f dhtinjector.jar ; rm -rf ~/SLOTH-EXP-TMP/INJECTOR_HOME/dhtinjector-log-* ;'
    launch_sloths = Remote(cmd,service_node, connection_params={'user': login}).run()    

    logger.info("Putting node addresses file %s into service node %s" % (args.nodes_address_file, service_node))
    cp = TaktukPut(service_node, [str(args.nodes_address_file)], remote_location=str(args.nodes_address_file)).run()
    
    injectorLogFileBase = 'injectorLog_' + str(args.experimentId)
    injectorLogFile = injectorLogFileBase + '.csv'
    checkFile = 'summary-' + str(args.experimentId) + '-' + str(args.dataMode) + '.log'
    dhtLogFile = 'dhtinjector-log-'+str(args.experimentId)+'-'+str(args.dataMode)+'.log'
    failuresFile = 'failures-'+str(args.experimentId)+'-'+str(args.dataMode)+'.log'

    cmd = '; '.join([
       'cd ~/SLOTH-EXP-TMP/INJECTOR_HOME/.'
      ,'cp ./config/injector.properties ./config/injector.properties.orig'
      ,'sed "s/peers.number.*/peers.number =' + str(args.nbNodes) + '/g" ./config/injector.properties > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'
      ,'sed "s/injection.mode.*/injection.mode = in_vivo/g" ./config/injector.properties > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'
      ,'sed "s:dht.nodesaddress.*:dht.nodesaddress = "'+args.nodes_address_file+'":g" ./config/injector.properties > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'
      ,'java -jar target/scala-2.10/dhtinjector.jar 2>&1 > ' + dhtLogFile + ' 0<&- 2>&-'
      ,'mv ./injectorLog.csv ' + injectorLogFile
      ,'./querycsv.py -i '+injectorLogFile+' -o '+failuresFile+' "SELECT * FROM '+injectorLogFileBase+' WHERE status == \\\"FAILURE\\\""'
      ,'tail -n 6 '+dhtLogFile+' > '+checkFile
      ,'./querycsv.py -i '+injectorLogFile+' "SELECT COUNT(*) AS total_failures FROM '+injectorLogFileBase+' WHERE status == \\\"FAILURE\\\"" >> '+checkFile 
      ,'./querycsv.py -i '+injectorLogFile+' "SELECT COUNT(*) AS get_failures FROM '+injectorLogFileBase+' WHERE status == \\\"FAILURE\\\" and operation == \\\"Get()\\\"">> '+checkFile
      ,'./querycsv.py -i '+injectorLogFile+' "SELECT COUNT(*) AS put_failures FROM '+injectorLogFileBase+' WHERE status == \\\"FAILURE\\\" and operation == \\\"Put()\\\"">> '+checkFile
    ])

    logger.info("%s/executing command %s" % (service_node, cmd))    
    launch_sloths = Remote(cmd,service_node, connection_params={'user': login}).run()
    logger.info("The injector has been launched.")

if __name__ == "__main__":
    try: 
        os.environ["INJECTOR_HOME"]
    except KeyError: 
        sys.exit("Please set the INJECTOR_HOME env variable")
    main()
