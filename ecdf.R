library(descr)
library(sqldf)

# Assumes cwd $SLOTH_HOME

processReadWriteLogs <- function(experimentId) {

    ##### PROCESS LAZY EXPERIMENT

    lazyLogFile <- paste(experimentId, "/lazy/analytics.log", sep="")
    lazyWriteQuery <- "SELECT * FROM file WHERE V2 = \"LWRITE\""
    lazyWriteData = read.csv.sql(lazyLogFile
      , header = FALSE
      , sep = ";"
      , sql = lazyWriteQuery)

    lazyWriteData$V1 <- as.numeric(strptime(lazyWriteData$V1, "%Y-%m-%d-%H:%M:%OS"))
    lazyWriteData$V1 <- lazyWriteData$V1 - lazyWriteData$V1[1]

    lazyReadQuery <- "SELECT * FROM file WHERE V2 = \"LREAD\""
    lazyReadData = read.csv.sql(lazyLogFile
      , header = FALSE
      , sep = ";"
      , sql = lazyReadQuery)

    lazyReadData$V1 <- as.numeric(strptime(lazyReadData$V1, "%Y-%m-%d-%H:%M:%OS"))
    lazyReadData$V1 <- lazyReadData$V1 - lazyReadData$V1[1]

    pdf(paste("lazyWritePlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(lazyWriteData$V1)
       , main=paste("#", experimentId, " ", "Lazy Write ECDF", sep="")
       , sub=paste("#Writes = ", length(lazyWriteData$V1))
       , xlab="Time since start [s]")
    dev.off()

    pdf(paste("lazyReadPlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(lazyReadData$V1)
       , main=paste("#", experimentId, " ", "Lazy Read ECDF", sep="")
       , sub=paste("#Reads = ", length(lazyReadData$V1))
       , xlab="Time since start [s]")
    dev.off()

    ##### PROCESS EAGER EXPERIMENT

    eagerLogFile <- paste(experimentId, "/eager/analytics.log", sep="")
    eagerWriteQuery <- "SELECT * FROM file WHERE V2 = \"EWRITE\""
    eagerWriteData = read.csv.sql(eagerLogFile
      , header = FALSE
      , sep = ";"
      , sql = eagerWriteQuery)

    eagerWriteData$V1 <- as.numeric(strptime(eagerWriteData$V1, "%Y-%m-%d-%H:%M:%OS"))
    eagerWriteData$V1 <- eagerWriteData$V1 - eagerWriteData$V1[1]

    eagerReadQuery <- "SELECT * FROM file WHERE V2 = \"EREAD\""
    eagerReadData = read.csv.sql(eagerLogFile
      , header = FALSE
      , sep = ";"
      , sql = eagerReadQuery)

    eagerReadData$V1 <- as.numeric(strptime(eagerReadData$V1, "%Y-%m-%d-%H:%M:%OS"))
    eagerReadData$V1 <- eagerReadData$V1 - eagerReadData$V1[1]    

    pdf(paste("eagerWritePlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(eagerWriteData$V1)
       , main=paste("#", experimentId, " ", "Eager Write ECDF", sep="")
       , sub=paste("#Writes = ", length(eagerWriteData$V1), sep="")
       , xlab="Time since start [s]")
    dev.off()

    pdf(paste("eagerReadPlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(eagerReadData$V1)
       , main=paste("#", experimentId, " ", "Eager Read ECDF", sep="")
       , sub=paste("#Reads = ", length(eagerReadData$V1), sep="")
       , xlab="Time since start [s]")
    dev.off()


    ### PLOT BOTH DATA SETS IN THE SAME PLOT
    pdf(paste("FullReadPlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(eagerReadData$V1)
	, pch = 8
	, verticals = TRUE
	, col = 'blue'
	, main=paste("#", experimentId, " ", "Eager / Lazy Read ECDF", sep="")
        , sub=paste("#Eager Reads = ", length(eagerReadData$V1), " ", "#Lazy Reads = ", length(lazyReadData$V1), sep="")
        , xlab="Time since start [s]"
    	)
    plot(ecdf(lazyReadData$V1), pch = 2 ,verticals = TRUE, add = TRUE, col = 'orange')

    legend(x="topleft"
	, legend=c("Eager", "Lazy"),
        col=c("blue","orange"), lwd=1, lty=c(1,2), 
        pch=c(8,2)
    )
 
    dev.off()

    ### PLOT BOTH DATA SETS IN THE SAME PLOT
    pdf(paste("FullWritePlot-", experimentId, ".pdf", sep=""))
    plot(ecdf(eagerWriteData$V1)
	, pch = 8
	, verticals = TRUE
	, col = 'blue'
	, main=paste("#", experimentId, " ", "Eager / Lazy Write ECDF", sep="")
        , sub=paste("#Eager Writes = ", length(eagerWriteData$V1), " ", "#Lazy Writes = ", length(lazyWriteData$V1), sep="")
        , xlab="Time since start [s]"
    	)
    plot(ecdf(lazyWriteData$V1), pch = 2 ,verticals = TRUE, add = TRUE, col = 'orange')

    legend(x="topleft"
	, legend=c("Eager", "Lazy"),
        col=c("blue","orange"), lwd=1, lty=c(1,2), 
        pch=c(8,2)
    )
 
    dev.off()


}
