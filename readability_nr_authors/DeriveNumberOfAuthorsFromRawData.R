# Get number of authors for each pmid from the raw data. 

#packages
library(rjson)

#List all journal-folders containing "searchresult"-files with nr-authors. Assumes that current directory is in parent folder.  
dirs<-list.dirs(path = './data/abstracts', recursive = F)

#df to store exluded pmids
pmindsExl<-c()

#df to store nr authors for every unique pmid
dfCounts<-c()

for(i in 1:length(dirs)){
  ipath<-paste0(dirs[i],"data/abstracts/id_author/forename_lastname_affiliation/searchresults")
  if(file.exists(ipath)){
    file<-fromJSON( file =  ipath)
    
    #make sure to keep missing values:
    df<-as.data.frame(cbind( as.numeric(as.character(unlist(file$pmid))) , unlist(as.character(file$forename)), unlist(as.character(file$lastname)) ))
    colnames(df)<-c("pmids","fornames","lastnames")
    
    #Make variables into char 
    a <- sapply(df, is.factor)
    df[a] <- lapply(df[a], as.character)
    
    #Make pmid-variable into numeric
    df$pmids<-as.numeric(df$pmids)
    
    #save and exlude pmids with "NA" in forename or lastname since these are non-people athors 
    dropIndx<-(is.na(df$fornames) & is.na(df$lastnames) )  
    
    pmindsExl<-rbind(pmindsExl,df[dropIndx,])
    
    #drop all matching pmids from this and previous "searchresults" that contain fore/last-names with "NA" in them
    dropThese<-match(df$pmids,pmindsExl,nomatch = F)
    df<-df[!dropThese,]  
    
    dfCounts<-rbind(dfCounts,as.data.frame(table(df$pmids)))
    
  }else{
    print(paste0('Could not find searchresult-file for ',dirs[i]))
  }
}

colnames(dfCounts)<-c("pmid","nrAuthors")

#Write dfCounts
write.csv(x = dfCounts,file =  "./data/abstracts/pmids_nrAuthors.csv")




