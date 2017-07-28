
import pandas as pd
import numpy as np
from collections import Counter
import os
import matplotlib.pyplot as plt
from math import ceil
import json

# This script deals with the example words (fig 5b in the article)
journalInfo = pd.read_csv('./JournalSelection/JournalSelection.csv')

# Simple analysis that goes through every (non-training data field) jounral and collects the percent difficult words for the science lists and the classic list for each year.

dataOfInterest = 'abstracttext,pubdate_year,pmid,articletitle,journal_title,keyword,doi'
# If dataframe, what is the index column (usally article or author)
dfId = 'article'

journalid = []
train_index = np.load('./jargon/pmidsTraining.npy')
ltext = []
wl = pd.read_csv('./jargon/scienceEasyWords.csv')
ew = wl['Training']

# To run all words, do this.
wrdList = ew
# For memory, I've only done the preselected ones. ALways froze when I tried to do it with ew above (with 8GB RAM).
wrdList = ['novel','robust','significant','distinct','moreover','therefore','primary','furthermore','influence','underlying','appears','suggesting']

for n in range(0, len(journalInfo)):

    #Create dataframe columns
    col = {}
    for e in wrdList:
        col[e] = []

    print(n)
    searchString = journalInfo.search[n].lower()
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ', '_')
    mDir = mDir.replace(',', '_')
    mDir = mDir.replace('\"', '')

    lDat=pd.read_json(mDir + 'lang.json')
    lDat.sort_index(inplace=True)
    lDat.replace('', np.nan, inplace=True)
    lDat.drop('doi', axis=1, inplace=True)
    lDat = lDat.dropna()
    #Dropping 2016 here for consistency with rest of text
    lDat = lDat.drop(lDat.index[lDat.year >= 2016])
    #Remove already used articles (training and verivation set)
    indMatch = set(lDat.pmid).intersection(np.squeeze(np.reshape(train_index, [np.prod(train_index.shape), 1])))
    if len(indMatch) > 0:
        indMatch = list(indMatch)
        for ind in indMatch:
            lDat = lDat.where(lDat.pmid != ind).dropna()
    #Loop through articles and get
    for aid in range(0, len(lDat)):
        text = lDat.strippedText.iloc[aid]
        text = text.replace('.', '') #Remove this again incase called by itself
        text = text.split()
        Ctxt = Counter(text)
        ltext = len(text)
        [col[e].append(Ctxt[e]/ltext) for e in wrdList]

    col['pubdate_year'] = list(map(int, lDat['year'].values))
    col['pmid'] = list(map(int, lDat['pmid'].values))

    with open(mDir + 'word_frequencies_sciencelist.json', 'w') as fp:
        json.dump(col,fp)

    fp.close()


if not os.path.exists('./jargon/examplewords'):
    os.mkdir('./jargon/examplewords')
#This is perhaps an unnecessary step, but it concatenates all the words into one file
for n in range(0, len(journalInfo)):

    #Parameters needed (if left blank, get_pubmeddata asks for response)
    #What to search pubmed with

    print(n)
    searchString = journalInfo.search[n].lower()
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ', '_')
    mDir = mDir.replace(',', '_')
    mDir = mDir.replace('\"', '')

    lDat=pd.read_json(mDir + 'word_frequencies_sciencelist.json')
    lDat.sort_index(inplace=True)

    if n == 0:
        for c in wrdList:
            if c == 'pmid':
                pass
            elif c == 'pubdate_year':
                pass
            else:
                df = pd.DataFrame(data={c:lDat[c],'pmid':lDat['pmid'],'pubdate_year':lDat['pubdate_year']})
                df.to_json('./jargon/examplewords/' + c + '.json')
    else:
        for c in wrdList:
            if c == 'pmid':
                pass
            elif c == 'pubdate_year':
                pass
            else:
                df=pd.read_json('./jargon/examplewords/' + c + '.json')
                df.sort_index(inplace=True)
                lDattmp = lDat[[c,'pubdate_year','pmid']]
                df=df.append(lDattmp)
                df.reset_index(inplace=True,drop=True)
                df.to_json('./jargon/examplewords/' + c + '.json')



n=0

fig,ax = plt.subplots(3,4)

for i in range(0,3):
    for j in range(0,4):

        wrd=wrdList[n]

        examplewordsDF = pd.read_json('./jargon/examplewords/' + wrd + '.json')
        examplewordsDF.sort_index(inplace=True)

        datavg = examplewordsDF.groupby(examplewordsDF.pubdate_year).mean()
        datavg['pubdate_year']=datavg.index

        # *100 to make into percentage
        ax[i,j].scatter(datavg.pubdate_year[65:], datavg[wrd][65:]*100,color='k',s=10)
        ax[i,j].set_xlim([1960,2015])
        ax[i,j].set_ylim([0, ceil(max(100*datavg[wrd][65:])*10000)/10000])
        ax[i,j].set_yticks([0, ceil(max(100*datavg[wrd][65:])*10000)/10000])
        ax[i,j].set_xticks(np.arange(1960, 2015, 10))
        ax[i,j].set_xticklabels([])
        ax[i,j].set_title(wrd)

        n+=1
fig.tight_layout()

fig.savefig('./figures/fig6b.pdf',format='pdf',dpi=600)
