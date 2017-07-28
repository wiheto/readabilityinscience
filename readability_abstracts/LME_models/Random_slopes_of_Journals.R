
#########################################################################
# Journal and Field specific analysis of readability v.s. time trend
#########################################################################

#Load packages
library(lmerTest)
library(tidyverse)

#specify path in and path out. Assumes that cd is the parent folder of the repo
path_model <- './data/LME_models'
path_journalData <- './JournalSelection/'
path_plotOut <- './figures'
#path_dataOut <- './article/elife/Source_data'

#Load LME model
attach(paste0(path_model,"/mod_flesch_yearFX_journalRX_is.Rda"))
attach(paste0(path_model,"/mod_NDC_yearFX_journalRX_is.Rda"))

#Load Journal ID data
JournalSelect<-readxl::read_excel(paste0(path_journalData,'S01_JournalSelection.xlsx'))

#Remove columns "subfields": i.e. duplicated rows of journals belonging to more than one subfield (journals can still belong to more than one "Field")
removeIdx<-duplicated(JournalSelect[,c('Field','Journal_Title_JCR')]) #find all row that have "Journal_Title_JCR" duplicates within a Field. 
JournalID_FieldName<-JournalSelect[!removeIdx,] #remove duplicates within the same field  

#Merge lang data and Journal/field ID dfs 
JournalID_FieldName<- data.frame(JournalID = JournalID_FieldName$journalID,
                                 JournalName = JournalID_FieldName$Journal_Title_JCR,
                                 Field = JournalID_FieldName$Field, 
                                 Subfield = JournalID_FieldName$Subfield)
  
JournalID_FieldName<-JournalID_FieldName[order(JournalID_FieldName$JournalID),]

#Extract random slopes and random intercepts 
randeff.FRE<-coef(mod_flesch_yearFX_journalRX_is) #same as using ranef(M) + grand-slope or grand-intercept
randeff.NDC<-coef(mod_NDC_yearFX_journalRX_is) #same as using ranef(M) + grand-slope or grand-intercept

#Fre
JournalID<-rownames(randeff.FRE$journalID)
randeff.FRE.dat<-as.data.frame(randeff.FRE$journalID)
randeff.FRE.dat$JournalID<-JournalID
randeff.FRE.dat<-plyr::rename(randeff.FRE.dat,c("year.c"="REbetas.FRE"))
randeff.FRE.dat<-plyr::rename(randeff.FRE.dat,c("(Intercept)"="Intercepts.FRE"))

#NDC
JournalID<-rownames(randeff.NDC$journalID)
randeff.NDC.dat<-as.data.frame(randeff.NDC$journalID)
randeff.NDC.dat$JournalID<-JournalID
randeff.NDC.dat<-plyr::rename(randeff.NDC.dat,c("year.c"="REbetas.NDC"))
randeff.NDC.dat<-plyr::rename(randeff.NDC.dat,c("(Intercept)"="Intercepts.NDC"))

#Merge FRE and NDC random slopes dfs
randeff.dat <- merge(randeff.NDC.dat,randeff.FRE.dat,by="JournalID")


##################################
# Journals specific plot of betas
##################################

#Merge will JournalSelect
randeff.dat.Journal <- merge(randeff.dat,JournalID_FieldName,by.x="JournalID", by.y="JournalID")

#Remove any duplicated journals
removeIdx <- duplicated(randeff.dat.Journal$JournalID)
randeff.dat.Journal <- randeff.dat.Journal[!removeIdx,] 
  
#Write csv for eLife source_data
#write.csv(x = randeff.dat.Journal,file = paste0(path_dataOut,'/Table1_supplement-fig2ab_journal_slopes.csv'),row.names = F)

#FRE: Plot each journal's random slope (with labels next to points mapping to a legend with all Journal-names)
randeff.dat.Journal <- randeff.dat.Journal[order(-randeff.dat.Journal$REbetas.FRE),] #sort FRE descending
randeff.dat.Journal$Rank.betas.FRE<-1:nrow(randeff.dat.Journal)
randeff.dat.Journal$Label.betas.FRE<-1:nrow(randeff.dat.Journal)

#Keep only each second label for legend (gets cluttered otherwise)  
keep.idx<-randeff.dat.Journal$Label.betas.FRE[c(TRUE,FALSE)]
keep.idx<-randeff.dat.Journal$Label.betas.FRE %in% keep.idx
randeff.dat.Journal$Label.betas.FRE[!keep.idx]<-""

FRE.Betas.journals.plot<-ggplot(data = randeff.dat.Journal,aes(x = Rank.betas.FRE, y = REbetas.FRE, label = Label.betas.FRE)) +
  geom_point() +
  geom_text(aes(label = Label.betas.FRE, size = 0.01), 
            hjust=-0.2, 
            vjust=-0.3,
            size=3) + 
  ylab('FRE: Journal specific slopes') + 
  xlab('Rank') + 
  theme_bw() +
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank()) 
  
ggsave(filename = paste0(path_plotOut,'/fig3-SUPPL1a.pdf'),plot = FRE.Betas.journals.plot,device = "pdf",width = 20/1.3,height = 10/1.3)

#Write legend for FRE random slopes for each journal
FRE.outLegend <- data.frame(Labels = randeff.dat.Journal$Label.betas.FRE,JournalNames=randeff.dat.Journal$JournalName)
#xlsx::write.xlsx(x = FRE.outLegend,file = paste0(path_plotOut,'/fig3-SUPPL1a_legend.pdf'),row.names = F)

#NDC: Plot each journal's random slope (with labels next to points mapping to a legend with all Journal-names)
randeff.dat.Journal <- randeff.dat.Journal[order(randeff.dat.Journal$REbetas.NDC),] #sort NDC descending
randeff.dat.Journal$Rank.betas.NDC<-1:nrow(randeff.dat.Journal)
randeff.dat.Journal$Label.betas.NDC<-1:nrow(randeff.dat.Journal)

#Keep only each second label for legend (gets cluttered otherwise)  
keep.idx<-randeff.dat.Journal$Label.betas.NDC[c(TRUE,FALSE)]
keep.idx<-randeff.dat.Journal$Label.betas.NDC %in% keep.idx
randeff.dat.Journal$Label.betas.NDC[!keep.idx]<-""

NDC.Betas.journals.plot<-ggplot(data = randeff.dat.Journal,aes(x = Rank.betas.NDC, y = REbetas.NDC, label = Label.betas.NDC)) +
  geom_point() +
  geom_text(aes(label = Label.betas.NDC, size = 0.01), 
            hjust=1.3, 
            vjust=-0.3,
            size=3) + 
  ylab('NDC: Journal specific slopes') + 
  xlab('Rank') + 
  theme_bw() +
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank()) 

ggsave(filename = paste0(path_plotOut,'/fig3-SUPPL1b.pdf'),plot = NDC.Betas.journals.plot,device = "pdf",width = 20/1.3,height = 10/1.3)

#Write legend for FRE random slopes for each journal
NDC.outLegend <- data.frame(Labels = randeff.dat.Journal$Label.betas.NDC,JournalNames=randeff.dat.Journal$JournalName)
#xlsx::write.xlsx(x = NDC.outLegend,file = paste0(path_plotOut,'/fig3-SUPPL1b_legend.pdf'),row.names = F)


######################################
# Fields specific plot of betas
##################################### 

#Merge with JournalID (contains Field info as well)
randeff.dat.Field <- merge(randeff.dat,JournalID_FieldName,by="JournalID")

#Summarize journal random slopes within Fields
RE.summary.Field<-randeff.dat.Field %>% 
  group_by(Field) %>%
  dplyr::summarise(meanBeta.FRE = mean(REbetas.FRE),
            seBetas.FRE = sd(REbetas.FRE)/sqrt(length(REbetas.FRE)),
            nBetas.Fre = length(REbetas.FRE),
            meanBeta.NDC = mean(REbetas.NDC),
            seBetas.NDC = sd(REbetas.NDC)/sqrt(length(REbetas.NDC)),
            nBetas.NDC = length(REbetas.NDC))

#Write FRE-NDC-Journal/Field data
#write.csv(x = RE.summary.Field,file = paste0(path_dataOut,'/fig3_ab_field_slopes_summary.csv'),row.names = F)

RE.summary.Field$Field<- as.character(RE.summary.Field$Field)
RE.summary.Field$Field[RE.summary.Field$Field=='Molecular Biology, Genetics & Biochemistry']<-'Molecular Biology,\nGenetics & Biochemistry'

#Plot FRE
RE.summary.Field <- RE.summary.Field[order(-RE.summary.Field$meanBeta.FRE),]
RE.summary.Field$Rank.betas.FRE <- 1:nrow(RE.summary.Field) 

FRE.Betas.fields.plot<-ggplot(data = RE.summary.Field,aes(x = Rank.betas.FRE, y = meanBeta.FRE, colour = Field)) +
  geom_errorbar(aes(ymin=meanBeta.FRE-seBetas.FRE, ymax=meanBeta.FRE+seBetas.FRE), colour="black", width=.1) +
  geom_point(size = 3) +
  ylab('FRE mean slopes') + 
  scale_x_discrete(limits=RE.summary.Field$Rank.betas.FRE,
                   labels = as.character(RE.summary.Field$Field[RE.summary.Field$Rank.betas.FRE])) + 
  theme_bw() + 
  theme(legend.position="none",
        axis.title.x=element_blank(),
        axis.text.x = element_text(angle = 45, hjust = 1)) 

ggsave(filename = paste0(path_plotOut,'/fig3a.svg'),plot = FRE.Betas.fields.plot,device = svg,width = 16,height = 16/1.618,units = "cm")


#Plot NDC
RE.summary.Field <- RE.summary.Field[order(RE.summary.Field$meanBeta.NDC),]
RE.summary.Field$Rank.betas.NDC <- 1:nrow(RE.summary.Field) 

NDC.Betas.fields.plot<-ggplot(data = RE.summary.Field,aes(x = Rank.betas.NDC, y = meanBeta.NDC, colour = Field)) +
  geom_errorbar(aes(ymin=meanBeta.NDC-seBetas.NDC, ymax=meanBeta.NDC+seBetas.NDC), colour="black", width=.1) +
  geom_point(size = 3) +
  ylab('NDC mean slopes') + 
  scale_x_discrete(limits=RE.summary.Field$Rank.betas.NDC,
                   labels = as.character(RE.summary.Field$Field[RE.summary.Field$Rank.betas.NDC])) + 
  theme_bw() + 
  theme(legend.position="none",
        axis.title.x=element_blank(),
        axis.text.x = element_text(angle = 45, hjust = 1)) 
 
ggsave(filename = paste0(path_plotOut,'/fig3b.svg'),plot = NDC.Betas.fields.plot,device = svg,width = 16,height = 16/1.618,units = "cm")


#Extract legend

Legend.plot <-ggplot(data = RE.summary.Field,aes(x = Rank.betas.NDC, y = meanBeta.NDC, colour = Field)) +
  geom_errorbar(aes(ymin=meanBeta.NDC-seBetas.NDC, ymax=meanBeta.NDC+seBetas.NDC), colour="black", width=.1) +
  geom_point(size = 3) +
  ylab('NDC mean slopes') + 
  xlab('Rank') + 
  theme_bw() + 
  theme(axis.text.x=element_blank(),
        axis.ticks.x=element_blank()) 

Legend.plot<-cowplot::get_legend(Legend.plot)
 
legend.out<-cowplot::plot_grid(Legend.plot)

ggsave(filename = paste0(path_plotOut,'/fig3_legend_to_1a_1b.svg'),plot = legend.out,device = svg,width = 16,height = 16/1.618,units = "cm")
