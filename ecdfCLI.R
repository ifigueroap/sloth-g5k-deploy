source("ecdf.R")
args <- commandArgs(trailingOnly = TRUE)
processReadWriteLogs(args[1])
