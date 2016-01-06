#!/usr/bin/python

from __future__ import print_function
import argparse
import os
import csv

parser = argparse.ArgumentParser(description="Run Batch Experiments in the Sloth system")
parser.add_argument('-f','--config-file', help="CSV file with configurations for each experiment", required=True)
#parser.add_argument('-h','--help', help="Display format for CSV file")

def main():
  
  args = parser.parse_args()
  print(args)

  with open(args.config_file) as experimentsFile:
    with open("./experiments.txt", "w") as bashExperimentsFile: 
	    configReader = csv.reader(experimentsFile, delimiter=';')

	    # skip the headers
	    next(configReader, None)

	    for config in configReader:
  		configStr = [
		    './runExperiment.sh in_vivo %s %s %s' % (config[0], config[1], config[2])
		  , '--duration %s' 	   % config[3] if config[3].strip() != '' else None
	          , '--nbObjects %s'	   % config[4] if config[4].strip() != '' else None
		  , '--objectMaxSize %s'   % config[5] if config[5].strip() != '' else None
		  , '--getPeriod %s' 	   % config[6] if config[6].strip() != '' else None
		  , '--putPeriod %s'	   % config[7] if config[7].strip() != '' else None
		  , '--removalPeriod %s'   % config[8] if config[8].strip() != '' else None
		  , '--crashPeriod %s' 	   % config[9] if config[9].strip() != '' else None
		  , '--removalDuration %s' % config[10] if config[10].strip() != '' else None
	          , '--crashDuration %s'   % config[11] if config[11].strip() != '' else None
		]

		configStr = [x for x in configStr if x is not None]
		print(' '.join(configStr), file=bashExperimentsFile)

  os.system("bash experiments.txt")


if __name__ == "__main__":
  main()
