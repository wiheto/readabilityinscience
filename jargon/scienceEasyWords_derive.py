import scipy as sp
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import nltk
import readabilityFunctions as txt


## DATA AND PARAMETERS

#Import original easy words
easy_words = open('./functions/NDCeasywords.txt', 'r').read().replace('\n', '')
easy_word_list = easy_words.lower().split()

journalInfo = pd.read_csv('./JournalSelection/JournalSelection.csv')
dataOfInterest = 'abstracttext,pubdate_year,pmid,articletitle,journal_title,keyword,doi'
#If dataframe, what is the index column (usally article or author)
dfId = 'article'

# This script performs the "double random method" for deriving the list.
# It dervies two subsets of the data (one training, one verification (hence double)), each evenly distributed over decades.

def createDifficultWordLists(wordVec, excludeOriginal='yes'):
    #Get frequency distributions of each words
    wordVecFD = nltk.FreqDist(wordVec)
    originalEasyWords = open('./functions/NDCeasywords.txt', 'r').read().replace('\n', '')
    originalEasyWords = originalEasyWords.lower().split()
    wordVecDat = pd.DataFrame(columns = {'wordList', 'wordInstances'})

    wordVecDat['wordList'] = [i[0] for i in wordVecFD.most_common()]
    wordVecDat['wordInstances'] = [i[1] for i in wordVecFD.most_common()]
    wordVecDat.drop(wordVecDat[wordVecDat.wordList == '.'].index, inplace=True)

    #Exlcude original list.
    if excludeOriginal == 'yes':
        wordVecDat = wordVecDat.where(wordVecDat.isin(originalEasyWords) == False).dropna()
    #Create a science and combined list (science + original).
    scienceEasyWords = wordVecDat.iloc[0:len(originalEasyWords)]
    scienceEasyWords = list(scienceEasyWords.wordList.values)
    return scienceEasyWords



## CREATE "EASY"/COMMON SCIENCE LIST
npd = 4000 #number of article per decade
decades = [1960, 1970, 1980, 1990, 2000, 2010]
cdat = pd.read_csv('./data/abstracts/concatenatedLangData.csv')
cdat = cdat.drop(cdat.index[cdat.year >= 2016]) #Drop 2016 out of the analysis which is still there >< (usually done at plotting, but now needs to be done as otherwise training set will include 2016)
i = 0
rind = 0
train_index = np.zeros([len(decades)*int(npd/2), 2])
np.random.seed(2016)
for startyear in decades:
    tmpdat = cdat.iloc[(cdat.year.values >= startyear) & (cdat.year.values < startyear+10)]
    print(startyear)
    tmpdatind = np.array(tmpdat['Unnamed: 0'])
    np.random.shuffle(tmpdatind)
    train_index[rind:rind+int(npd/2), 0] = tmpdat.pmid.ix[tmpdatind[0:int(npd/2)]]
    train_index[rind:rind+int(npd/2), 1] = tmpdat.pmid.ix[tmpdatind[int(npd/2):npd]]
    i = i + npd
    rind = rind + int(npd/2)
    print(len(tmpdat))

np.save('./jargon/pmidsTraining.npy', train_index)


train_index = np.load('./jargon/pmidsTraining.npy')

wordVec1 = ''
wordVec2 = ''
for n in range(0, len(journalInfo)):
    print('serarching journal: ' + str(n))
    searchString = journalInfo.search[n].lower()
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + './data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ', '_')
    mDir = mDir.replace(',', '_')
    mDir = mDir.replace('\"', '')

    lDat = pd.read_json(mDir + 'lang.json')
    lDat = lDat.drop(lDat.index[lDat.year >= 2016]) #Drop 2016 here as well
    indMatch = set(lDat.pmid).intersection(train_index[:,0])
    if len(indMatch) > 0:
        indMatch = list(indMatch)
        for ind in indMatch:
            wordVec1=wordVec1 + lDat.strippedText.where(lDat.pmid == ind).dropna().str.cat().lower()
    lDat = lDat.drop(lDat.index[lDat.year >= 2016]) #Drop 2016 here as well
    indMatch = set(lDat.pmid).intersection(train_index[:, 1])
    if len(indMatch) > 0:
        indMatch = list(indMatch)
        for ind in indMatch:
            wordVec2 = wordVec2 + lDat.strippedText.where(lDat.pmid == ind).dropna().str.cat().lower()


wordVec1 = wordVec1.replace('.','')
wordVec1 = wordVec1.split()
scienceEasyWords_list1 = createDifficultWordLists(wordVec1)
wordVec2 = wordVec2.replace('.','')
wordVec2 = wordVec2.split()
scienceEasyWords_list2 = createDifficultWordLists(wordVec2)
#combinedList=createDifficultWordLists(wordVec,excludeOriginal='no') <- we didn't use this

ew = pd.DataFrame(columns={'Training', 'Verification'})
ew.Training = scienceEasyWords_list1
ew.Verification = scienceEasyWords_list2



ew.to_csv('./jargon/scienceEasyWords.csv')
