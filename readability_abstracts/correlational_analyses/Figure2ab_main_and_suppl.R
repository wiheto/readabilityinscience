#################
# Load packages #
#################
library(ggplot2)
library(ggthemes)
library(data.table)
library(tidyr)

###################################################
# Plot mean readability over years - main figures #
###################################################

#get data, calc means over years, and prepare data for plotting

path<-'./data/abstracts'
pathFIG<-'./figures/'


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

#Plots: 
dfPlot<-(cbind(rownames(meanFlesch),meanNDC,sdNDC,meanFlesch,sdFlesch))
dfPlot<-apply(dfPlot, 2, as.numeric)
dfPlot<-as.data.frame(dfPlot)
colnames(dfPlot)[1]<-'year'


## Plot without marginal histogram
#Flesch
scatterFlesch<-ggplot(data = dfPlot,aes(year,meanFlesch)) + 
  geom_point(col="darkblue") + 
  #ggthemes::theme_few() + 
  theme_bw() + 
  #geom_smooth(method = 'lm',se = F, col="grey20") + 
  xlab("Year") + 
  ylab("Readability (FRE)") + 
  scale_x_continuous(breaks= seq(1880,2010,by = 20)) +
  scale_y_continuous(breaks= seq(10,40,by = 10))


ggsave(filename =paste0(pathFIG,"/fig2a.svg"),plot = scatterFlesch,device = svg,width =16, height = 16/1.618, units = "cm")

#NDC
scatterNDC<-ggplot(data = dfPlot,aes(year,meanNDC)) + 
  geom_point(col="darkred") + 
  #ggthemes::theme_few() + 
  theme_bw() + 
  #geom_smooth(method = 'lm',se = F, col="grey20") + 
  xlab("Year") + 
  ylab("Readability (NDC)") + 
  scale_x_continuous(breaks= seq(1880,2010,by = 20)) 

ggsave(filename =paste0(pathFIG,"/fig2b.svg"),plot = scatterNDC,device = svg,width =16, height = 16/1.618, units = "cm")


################################################
# Same plots on the none preprocessed data     #
################################################

#get data, calc means over years, and ready it for plotting

file<-'concatenatedLangData_nopreproSMALL.csv'

concatDat.noPrePro<-data.table::fread(paste0(path,'/',file))

concatDat.noPrePro<-as.data.frame(concatDat.noPrePro)
concatDat.noPrePro<-concatDat.noPrePro[concatDat.noPrePro$year<2016,]
concatDat.noPrePro<-concatDat.noPrePro[!is.na(concatDat.noPrePro$flesch),]

nrow(concatDat.noPrePro)  

#get mean and sd readbility per year 
meanNDC <-with(data = concatDat.noPrePro, tapply(NDC, year, mean))
sdNDC <-with(data = concatDat.noPrePro, tapply(NDC, year, sd))

meanFlesch <-with(data = concatDat.noPrePro, tapply(flesch, year, mean))
sdFlesch <-with(data = concatDat.noPrePro, tapply(flesch, year, sd))

#Pearson r FRE
cor.test(as.numeric(rownames(meanFlesch)),meanFlesch,method = "pearson" )

#Pearson r NDC 
cor.test(as.numeric(rownames(meanNDC)),meanNDC,method = "pearson" )

#Plots: 
dfPlot<-(cbind(rownames(meanFlesch),meanNDC,sdNDC,meanFlesch,sdFlesch))
dfPlot<-apply(dfPlot, 2, as.numeric)
dfPlot<-as.data.frame(dfPlot)
colnames(dfPlot)[1]<-'year'

#Flesch
scatterFlesch<-ggplot(data = dfPlot,aes(year,meanFlesch)) + 
  geom_point(col="darkblue") + 
  #ggthemes::theme_few() + 
  theme_bw() + 
  #geom_smooth(method = 'lm',se = F, col="grey20") + 
  xlab("Year") + 
  ylab("Readability (FRE)") + 
  scale_x_continuous(breaks= seq(1880,2010,by = 20)) +
  scale_y_continuous(breaks= seq(10,40,by = 10))

ggsave(filename =paste0(pathFIG,"/fig2a_SUPPL.svg"),plot = scatterFlesch,device = svg,width =16, height = 16/1.618, units = "cm")

#NDC
scatterNDC<-ggplot(data = dfPlot,aes(year,meanNDC)) + 
  geom_point(col="darkred") + 
  #ggthemes::theme_few() + 
  theme_bw() + 
  #geom_smooth(method = 'lm',se = F, col="grey20") + 
  xlab("Year") + 
  ylab("Readability (NDC)") + 
  scale_x_continuous(breaks= seq(1880,2010,by = 20)) 

ggsave(filename =paste0(pathFIG,"/fig2b_SUPPL.svg"),plot = scatterNDC,device = svg,width =16, height = 16/1.618, units = "cm")


