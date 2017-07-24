
import pandas as pd
import numpy as np
import readabilityFunctions as txt
import os

journalInfo=pd.read_csv('./JournalSelection/JournalSelection.csv')
dataOfInterest = 'abstracttext,pubdate_year,pmid,articletitle,journal_title,keyword,doi'
#If dataframe, what is the index column (usally article or author)
dfId = 'article'

#SImple analysis that goes through every (non-training data field) jounral and collects the percent difficult words for the science lists and the classic list for each year.
year=[]
percentScienceEasyWords2949=[]
percentGeneralScienceJargon=[]
percentClassicEasyWords2949=[]
pmid=[]
journalid=[]
train_index=np.load('./jargon/pmidsTraining.npy')

ew = pd.read_csv('./jargon/scienceEasyWords.csv')
ew_pruned = pd.read_csv('./jargon/jargonListFinal.csv')

scienceEasyWords2949 = list(ew.Training)
generalScienceJargon = list(ew_pruned['word'].where(ew_pruned['generalScienceJargon']==1).dropna())

for n in range(0,len(journalInfo)):
    #Parameters needed (if left blank, get_pubmeddata asks for response)
    #What to search pubmed with
    print(n)
    searchString = journalInfo.search[n].lower()
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')

    lDat=pd.read_json(mDir + 'lang.json')
    lDat.sort_index(inplace=True)
    lDat.replace('', np.nan, inplace=True)
    lDat.drop('doi', axis=1, inplace=True)
    lDat=lDat.dropna()
    lDat=lDat.drop(lDat.index[lDat.year>=2016]) #Dropping 2016 here for consistency with rest of text
    #Remove already used in training or verication dataset
    indMatch= set(lDat.pmid).intersection(np.squeeze(np.reshape(train_index, [np.prod(train_index.shape), 1])))
    if len(indMatch)>0:
        indMatch=list(indMatch)
        for ind in indMatch:
            lDat=lDat.where(lDat.pmid!=ind).dropna()
    #Loop through articles and get
    for aid in range(0,len(lDat)):
        percentClassicEasyWords2949.append(100-txt.difficult_words(lDat.strippedText.iloc[aid],output='percent'))
        percentGeneralScienceJargon.append(100-txt.difficult_words(lDat.strippedText.iloc[aid],generalScienceJargon,output='percent'))
        percentScienceEasyWords2949.append(100-txt.difficult_words(lDat.strippedText.iloc[aid],scienceEasyWords2949,output='percent'))
    year = year + list(lDat.year)
    pmid = pmid + list(lDat.pmid)
    journalid = journalid + list(np.zeros(len(lDat))+n)



easywords=pd.DataFrame()
easywords['classic2949'] = percentClassicEasyWords2949
easywords['science2949'] = percentScienceEasyWords2949
easywords['generalScienceJargon'] =percentGeneralScienceJargon

#dat.NDC_classic = [i[0] for i in NDC_classic]
#dat.NDC_comb = [i[0] for i in NDC_combined]
easywords['year'] = year
easywords['journalID'] = journalid
easywords['pmid'] = pmid
easywords.to_json('./jargon/lang_generalsciencejargon.json')
