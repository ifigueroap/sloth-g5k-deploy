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
parser.add_argument('--nodes_address_file'
                    , help="Absolute pathname to the file indicating the peer addresses"
                    , required=True
                    , metavar="F"
                    , default = "./configuration/nodes_address.txt")
parser.add_argument('-s', '--service_node', help="name of the node where the injector will be executed", required=True)
parser.add_argument('-u', '--user', help="login of the user launching the script")

# Optional parameters to specify experiment configuration

parser.add_argument('--duration', type=int, help="Duration of injection in seconds. Defaults to injector.properties value", required=False)
parser.add_argument('--nbObjects', type=int, help="Number of objects. Defaults to injector.properties value", required=False)
parser.add_argument('--objectMaxSize', type=int, help="Maximum size of objects. Defaults to injector.properties value", required=False)
parser.add_argument('--getPeriod', type=int, help="Period for Get requests. Defaults to injector.properties value", required=False)
parser.add_argument('--putPeriod', type=int, help="Period for Put requests. Defaults to injector.properties value", required=False)
parser.add_argument('--removalPeriod', type=int, help="Period for voluntary removals. Defaults to injector.properties value", required=False)
parser.add_argument('--crashPeriod', type=int, help="Period for failures. Defaults to injector.properties value", required=False)
parser.add_argument('--removalDuration', type=int, help="Length in seconds for voluntary removals. Defaults to injector.properties value", required=False)
parser.add_argument('--crashDuration', type=int, help="Length in seconds for failures. Defaults to injector.properties value", required=False)

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
    
    injectorLogFileBase = 'injectorLog_' + str(args.experimentId) + '_' + str(args.dataMode)
    injectorLogFile = injectorLogFileBase + '.csv'
    checkFile = 'summary_' + str(args.experimentId) + '_' + str(args.dataMode) + '.log'
    dhtLogFile = 'dhtinjector_log_'+str(args.experimentId)+'_'+str(args.dataMode)+'.log'
    failuresFile = 'failures_'+str(args.experimentId)+'_'+str(args.dataMode)+'.log'

    #
    # Mandatory replacements in injector.properties file
    #
    cmdLines = [
       'cd ~/SLOTH-EXP-TMP/INJECTOR_HOME/.'
      ,'sed "s/peers.number.*/peers.number = ' + str(args.nbNodes) + '/g" ./config/injector.properties.template > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'
      ,'sed "s/injection.mode.*/injection.mode = in_vivo/g" ./config/injector.properties > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'
      ,'sed "s:dht.peersaddress.*:dht.peersaddress = "'+args.nodes_address_file+'":g" ./config/injector.properties > /tmp/injector.properties'
      ,'cp /tmp/injector.properties ./config/injector.properties'    
    ]

    #
    # Optional replacements in injector.properties file, according to command-line arguments
    #
    if (args.duration is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.duration.*/injector.duration = ' + str(args.duration) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.nbObjects is not None):
        cmdLines = cmdLines + [
              'sed "s/objects.number.*/objects.number = ' + str(args.nbObjects) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.objectMaxSize is not None):
        cmdLines = cmdLines + [
              'sed "s/object.maxsize.*/objects.maxsize = ' + str(args.objectMaxSize) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.getPeriod is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.getperiod.*/injector.getperiod = ' + str(args.getPeriod) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.putPeriod is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.putperiod.*/injector.putperiod = ' + str(args.putPeriod) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.removalPeriod is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.removalperiod.*/injector.removalperiod = ' + str(args.removalPeriod) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.crashPeriod is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.crashperiod.*/injector.crashperiod = ' + str(args.crashPeriod) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.removalDuration is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.removalduration.*/injector.removalduration = ' + str(args.removalDuration) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    if (args.crashDuration is not None):
        cmdLines = cmdLines + [
              'sed "s/injector.crashduration.*/injector.crashduration = ' + str(args.crashDuration) + '/g" ./config/injector.properties > /tmp/injector.properties'
            , 'cp /tmp/injector.properties ./config/injector.properties'
        ]

    ###############################################################################################
    #
    # Command to actually run the injector, loading the ./config/injector.properties file
    #

    cmdLines = cmdLines + [
        'java -DdataMode='+ str(args.dataMode)+ ' -DexperimentId='+ str(args.experimentId) +' -jar target/scala-2.10/dhtinjector.jar 2>&1 > ' + dhtLogFile + ' 0<&- 2>&-'
    ]

    cmd = ";".join(cmdLines)
    logger.info("%s/executing command %s" % (service_node, "\n".join(cmdLines)))    
    launch_sloths = Remote(cmd,service_node, connection_params={'user': login}).run()    

    ##############################################################################################
    #
    # Execute remote commands to obtain total count of failures
    #
    
    cmdLines = [
       'cd ~/SLOTH-EXP-TMP/INJECTOR_HOME/.'
      ,'mv ./injectorLog.csv ' + injectorLogFile + ' 2>&1 > /tmp/errorFile'
      ,'./querycsv.py -i '+injectorLogFile+' -o '+failuresFile+' "SELECT * FROM '+injectorLogFileBase+' WHERE status == \\\"FAILURE\\\""'

      # Grab last lines from dhtLogFile with the summary data
      ,'tail -n 23 '+dhtLogFile+' > '+checkFile
      ,'./querycsv.py -i '+injectorLogFile+" 'SELECT COUNT(*) AS total_failures FROM " + injectorLogFileBase + " WHERE status == \"FAILURE\"' >>" + checkFile
      ,'./querycsv.py -i '+injectorLogFile+" 'SELECT COUNT(*) AS get_failures FROM "   + injectorLogFileBase + " WHERE status == \"FAILURE\" and operation == \"Get()\"' >> " + checkFile
      ,'./querycsv.py -i '+injectorLogFile+" 'SELECT COUNT(*) AS put_failures FROM "   + injectorLogFileBase + " WHERE status == \"FAILURE\" and operation == \"Put()\"' >> " + checkFile
    ]

    cmd = ";".join(cmdLines)
    logger.info("%s/executing command %s" % (service_node, "\n" + "\n".join(cmdLines)))
    launch_sloths = Remote(cmd,service_node, connection_params={'user': login}).run()
    
    logger.info("The injector has been launched.")

if __name__ == "__main__":
    try: 
        os.environ["INJECTOR_HOME"]
    except KeyError: 
        sys.exit("Please set the INJECTOR_HOME env variable")
    main()
