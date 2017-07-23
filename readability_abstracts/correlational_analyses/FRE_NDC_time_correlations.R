#################
# Load packages #
#################
library(data.table)

###############################################################################################
# Calculate correlations between mean FRE and year, mean NDC and year and between FRE and NDC
###############################################################################################

#get data, calc means over years, and prepare data for plotting
#Get OS and setwd

path<-'./data/abstracts'
file<-'concatenatedLangDataSMALL.csv'

concatDat<-data.table::fread(paste0(path,'/',file))

concatDat<-as.data.frame(concatDat)
concatDat<-concatDat[concatDat$year<2016,]
concatDat<-concatDat[!is.na(concatDat$flesch),]

nrow(concatDat)

#get mean and sd readbility per year 
meanNDC <-with(data = concatDat, tapply(NDC, year, mean))
sdNDC <-with(data = concatDat, tapply(NDC, year, sd))

meanFlesch <-with(data = concatDat, tapply(flesch, year, mean))
sdFlesch <-with(data = concatDat, tapply(flesch, year, sd))

#Pearson r FRE
cor.test(as.numeric(rownames(meanFlesch)),meanFlesch,method = "pearson" )

#Pearson r NDC
cor.test(as.numeric(rownames(meanNDC)),meanNDC,method = "pearson" )

#FRE vs NDC
cor.test(concatDat$flesch,concatDat$NDC)
