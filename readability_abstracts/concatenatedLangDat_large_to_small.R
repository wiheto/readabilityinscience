#Create concatenatedLangDataSMALL.csv file by calculating summed sylCount for each abstract and stripping the full file of 'wordLength' and 'DiffWord_lst'
# This script also merges concatData with "./pubmeddata/pmids_nrAuthors.csv" and outputs everything in "./pubmeddata/concatenatedLangDataSMALL.csv" or "./pubmeddata/concatenatedLangData_nopreproSMALL.csv"

#Load packages
library(data.table)
library(tidyverse)

#Read Nr Authors data
dat.nrAuthors <- fread(paste0('./data/abstracts/pmids_nrAuthors.csv'))
dat.nrAuthors$pmid<-as.numeric(as.character(dat.nrAuthors$pmid))
colnames(dat.nrAuthors)

###################
# Preprocess Data
###################

dat.large<-fread(paste0('./data/abstracts/concatenatedLangData.csv'))
colnames(dat.large)

#Create average syllable count
syl2sylCount <- function(x) {
  sum(as.numeric(strsplit(gsub('[\\[\\]]', '', as.character(x), perl = T), ',')[[1]]))
}
  
dat.large <- dat.large %>%
  mutate(sylCount_total = map_dbl(sylCount, syl2sylCount ) )


#Subset merged Lang file  (delete "DiffWord_lst" and "wordLength" and "sylCount" columns)
dat.small <- select(dat.large, -V1, -DiffWord_lst, -wordLength, -sylCount, sylCount=sylCount_total)

#Write
write.csv(dat.small,paste0('./data/abstracts/concatenatedLangDataSMALL.csv'),row.names = F)

######################
# Non-Preprocess Data
######################

#Read in non-preprocessed data
dat.large<-fread(paste0('./data/abstracts/concatenatedLangData_noprepro.csv'))
colnames(dat.large)

#Create average syllable count
dat.large <- dat.large %>%
  mutate(sylCount_total = map_dbl(sylCount, syl2sylCount ) )

#Subset merged Lang file  
dat.small <- select(dat.large, -V1, -DiffWord_lst, -wordLength, -sylCount, sylCount=sylCount_total)

#Write
write.csv(dat.small,paste0('./data/abstracts/concatenatedLangData_nopreproSMALL.csv'),row.names = F)


