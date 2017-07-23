

#%%
#md

"""
## Calculate Readability

This file calculates the FRE and NDC for all journals in the JournalSelection csv. All files are saved in ./data/abstracts as "lang.json".

Files are also concatenating into one big file (just for ease of process). The script "concatenatedLangDat_large_to_small.R" make these files even smaller.

Non preprocessed language files are also created and concatenated.

Main calculation functions are found in ./functions/readabilityFunctions.py

Treetagger needs to be installed with english tagger version.
"""

#%%
#md
"""
__One variable needs to be set in this file. repo_directory (next cell block) which points to the repo main directory__

"""

#%%

repo_directory = '/Path/to/readabilityinscience/'

#%%

import os
os.chdir(repo_directory)

import numpy as np
import pandas as pd
import functions.dataminingfunctions as dmf
import functions.readabilityFunctions as rf
import treetaggerwrapper


#%%


journalInfo=pd.read_csv('./JournalSelection/JournalSelection.csv')




#%%
#md
"""
Define treetagger.
(Note, treetagger definitions can vary between windows and linux. Linux was used in the analysis. Using windows may see minor differences in parsing)
"""

#%%
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')



#%%
#md
"""
Calculate readability
"""
#%%


for n in range(0,len(journalInfo)):
    #What to search pubmed with
    searchString = journalInfo.search[n].lower()
    print(' --- Calculating Readability: ' + searchString + '. term: ' + str(n) + ' ---')
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/./data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')

    rf.analyze(mDir + 'searchresults',mDir + 'lang.json','abstracttext',{'pubdate_year<>year','pmid','doi'},tagger)


#%%
#md
"""
Calculate readability (without preprocessing of data)
"""
#%%

tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')
for n in range(0,len(journalInfo)):
    #What to search pubmed with
    searchString = journalInfo.search[n].lower()
    print(' --- Calculating Readability: ' + searchString + '. term: ' + str(n) + ' ---')
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/./data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')
    mDir = mDir
    try:
        os.mkdir(mDir + '/noprepro/')
    except:
        pass
    rf.analyze(mDir + 'searchresults',mDir+'/noprepro/lang.json','abstracttext',{'pubdate_year<>year','pmid','strippedText','wordLength','wordCount','sentenceCount','sylCount','flesch','NDC','PercDiffWord','doi','DiffWord_lst'},tagger,doPreprocessing=0)




#%%
#md
"""
Concatenate the readability files
"""
#%%

for n in range(0,len(journalInfo)):
    #Parameters needed (if left blank, get_./data/abstracts asks for response)
    #What to search pubmed with
    searchString = journalInfo.search[n].lower()
    print(' ---Concatenating: ' + searchString + '. term: ' + str(n) + ' ---')

    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/./data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')

    lDat=pd.read_json(mDir + 'lang.json')
    lDat.sort_index(inplace=True)
    lDat.drop('strippedText',1,inplace=True)

    newColumns = {'journalID','flesch','PercDifWord','sylCount','sentenceCount','wordCount','year','articleID'}
    lDat['journalID']=np.zeros(len(lDat))+n
    lDat['articleID']=lDat.index

    if n==0:
        cDat=lDat
    else:
        cDat=cDat.append(lDat)


# Reset index and save
cDat.reset_index(inplace=True)
cDat.to_csv(os.getcwd() + '/./data/abstracts/concatenatedLangData.csv')
cDat.to_pickle(os.getcwd() + '/./data/abstracts/concatenatedLangData.pkl')


#%%
#md
"""
Concatenate the non-preprocessed readability files
"""
#%%

# Same as part for but for the unpreprocessed data
for n in range(0,len(journalInfo)):
    #Parameters needed (if left blank, get_./data/abstracts asks for response)
    #What to search pubmed with
    searchString = journalInfo.search[n].lower()
    print(' ---Concatenating: ' + searchString + '. term: ' + str(n) + ' ---')
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/./data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')

    lDat=pd.read_json(mDir + '/noprepro/lang.json')
    lDat.sort_index(inplace=True)
    lDat.drop('strippedText',1,inplace=True)

    newColumns = {'journalID','flesch','PercDifWord','sylCount','sentenceCount','wordCount','year','articleID'}
    lDat['journalID']=np.zeros(len(lDat))+n
    lDat['articleID']=lDat.index

    if n==0:
        cDat=lDat
    else:
        cDat=cDat.append(lDat)

# Reset index and save
cDat.reset_index(inplace=True)
cDat.to_csv(os.getcwd() + '/./data/abstracts/concatenatedLangData_noprepro.csv')
cDat.to_pickle(os.getcwd() + '/./data/abstracts/concatenatedLangData_noprepro.pkl')
