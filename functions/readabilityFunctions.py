# -*- coding: utf-8 -*-
"""

This file contains all
Requires: curses, nltk, pandas, treetagwrapper
Also requires abstract_cleanup and NDCeasywords.txt
The NDCeasywords.txt list originates from the textstat python package. - https://github.com/shivam5992/textstat

"""

import curses #For windows: download and pip install curses from http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
from curses.ascii import isdigit
import nltk
from nltk.corpus import cmudict
import re
import time
import pandas as pd
import numpy as np
import treetaggerwrapper
import functions.abstract_cleanup as qc
import os


d = cmudict.dict()
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')

#Load easy word list
easywordpath=os.path.join(os.path.dirname(__file__), 'NDCeasywords.txt')
easy_words = open(easywordpath,'r').read().replace('\n','').lower()
easy_word_list = easy_words.split()

def difficult_words(text,diffwordlist=easy_word_list,output='Num&List'):
    #Output can either be NumList (number difficult words and List of difficult words) Or it can be 'percent'
    text=text.replace('.','') #Remove this again incase called by itself
    text = text.split()
    diff_words = []
    for value,i in zip(text, range(len(text)) ): #loop through two things at once because python is haxor
        if value not in diffwordlist:
            diff_words.append(value)
    if output == 'Num&List':
        return len(diff_words), list(set(diff_words))
    elif output == 'percent':
        return len(diff_words)/len(text)*100

def NDC(text, wc, sc,diffwordlist=easy_word_list):
    '''
    Function calcualted NDC of a text (as string). Give word could and sentence could (possible extension, add this automatically to be calculated).
    diffwordlist default is the one above from the NDC default.
    Output is NDC, percent difficult words, list of difficult words
    '''
    text=text.replace('.','')
    numDifWords,difWordsList=difficult_words(text,diffwordlist)
    if wc > 0:
        perfectDificultWords = (numDifWords)/(wc)*100 #percentage diff word in text
        if perfectDificultWords > 5:         #if percent diff words > 5
                score = (0.1579 * perfectDificultWords) + (0.0496 * wc/sc + 3.6365)
        else:
                score = (0.1579 * perfectDificultWords) + (0.0496 * wc/sc)
        return round(score, 2),perfectDificultWords, difWordsList
    else:
        return np.nan, np.nan, np.nan


# TO be modified from recent update to other functions
#def diffwords_percent(text, diffwordlist=easy_word_list):
#    text=text.replace('.','')
#    word_count = len(text.split())
#    count = word_count - difficult_words(text,diffwordlist)
#    if word_count > 0:
#        per = float(count)/float(word_count)*100 #percentage diff word in text
#    else:
#        return 'NaN'
#    difficult_wordsP = 100-per
#    return difficult_wordsP


def count_syllables(wrd,d=cmudict.dict()):
    '''
    Count syllables works in two steps. First it searches a dictionary wherer the answer is usually better. If missing from the dictionary a heuristic is applied where the vowels are counted.
    Requires: nltk and a dictionary. To get cmudict, install NLTK and run "from nltk.corpus import cmudict"
    '''
    #Make sure word contains a vowel before sending to dictionary
    restr=re.compile('[AEIOUYaeiouy]')
    if restr.search(wrd):
        cnt=count_syllables_primary(wrd,d)
        #If 0 from above function, go to secondary function
        if cnt==0:
            cnt=count_syllables_secondary(wrd)
        #If multiple syllable alternatives exist, return the largest.
        if type(cnt) is list:
            sylCount=max(cnt)
        else:
            sylCount=cnt
    else:
        sylCount = 0
    return sylCount


def count_syllables_primary(word,d):
    try:
        return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
    except:
        return 0

def count_syllables_secondary(word):
    # Adapted from Akkana Peck http://shallowsky.com.
    vowels = ['a', 'e', 'i', 'o', 'u']
    on_vowel = False
    syl = 0
    lastchar = None
    word = word.lower()
    try:
        for c in word:
            is_vowel = c in vowels
            if on_vowel == None:
                on_vowel = is_vowel
            # y is a special case
            if c == 'y':
                is_vowel = not on_vowel
            if is_vowel:
                if not on_vowel:
                    # We weren't on a vowel before.
                    # Seeing a new vowel bumps the syllable count.
                    syl += 1
            on_vowel = is_vowel
            lastchar = c
        if word[-1] == 'y' and not on_vowel:
            syl += 1
    except:
        syl=0
    return [syl]



#TO DO. Get a row in trends which has different flesch score. Go through this file and old file and find the difference.
def lang_prepropipeline(dataIn,tagger):
    text=qc.cleanup_pretagger_all(dataIn)
    text=tagger.tag_text(text,notagdns=True) #Body or abstract text - specified in input variable
                #End of sentence
    isSent=re.compile('.*\\tSENT\.*')
    isSymbol=re.compile('.*\\tSYM\.*')
    isPos=re.compile('.*\\tPOS\.*')
    #Is other puncputation
    isPunct=re.compile('.\\t[^\w\s]\\.*')
    #Is word
    isWord=re.compile('^[&\w-]*')
    #Go through treetagger ouput and only inculed sentence ends and words
    #This is a little messy. Also adds some additional treetagger cautions
    textout=[]
    for w in text:
        if isSent.match(w):
            textout.append('.')
        elif isPunct.match(w) or isSymbol.match(w) or isPos.match(w):
            tmp=1 #Do nothing
        elif isWord.match(w):
            wrd=isWord.findall(w)[0]
            if (len(wrd)>1 or wrd=='a' or wrd=='A' or wrd=='I' or wrd=='.') and wrd.lower() != 'replaced-url' and wrd.lower() != 'replaced-ip' and wrd.lower() != 'replaced-email':
                textout.append(wrd)

    return textout

def lang_minimalprepropipeline(text):
    #Convert terminal punctuation to periods
    text=text.replace('?','.')
    text=text.replace('!','.')
    text=text.replace('.',' . ')
    if text[-1] != '.':
        text = text + ' .'
    text=text.split()
    return text

def countWordsSentSyl(text,ignoreSingleSentences=1):
    '''
    This funciton is the "main" function for calculating language measures.
    It goes through each word in a list of words (['text', 'looks', 'like' ,'this','.'])
    Returns word count, sentence count, the text that was used (one word sentence will be excluded), and word length.
    '''
    remainingText=[]
    wordLength=[]
    sylCount=[]
    sc=0 #sentenceCountIndex
    wc=0 #wordCountIndex
    wordCountInSentence = 0 #This needs to be greater than 1 o increase sentences
    for wrd in text:
        if wrd=='.' and wordCountInSentence>0:
            #Sentences must have at least one word in. Delete last input if only one word.
            if wordCountInSentence==1 and ignoreSingleSentences==1:
                wc=wc-1
                remainingText = remainingText[:-1]
                sylCount = sylCount[:-1]
                wordCountInSentence = 0
            else:
                remainingText.append('.')
                sc=sc+1
                wordCountInSentence = 0
        else:
            syl=count_syllables(wrd,d) #syl = number of syllables from count syllables. 0 if nothing found.
            if syl>0: #Final check to make sure there is at least one syllable
                wc=wc+1
                wordLength.append(len(wrd))
                sylCount.append(syl)
                remainingText.append(wrd)
                wordCountInSentence = wordCountInSentence +1
    return wc, sc, sylCount, remainingText, wordLength

def FRE(wc,sc,sylCount):
    return 206.835-1.015*(wc/sc)-84.6*(sum(sylCount)/wc)   #calc Flesch-Ease Index

#Main Function.
# Calculates wordlength, cordcount, number of sentences, syllable length and Flesch and NDC on a stripped text (aslo saves this)
# As of now this function only analyses the full text, and not the abstract-text-column from path.
def analyze(path,spath,textType='abstracttext',columnList={'doi','pmid','pubdate_year<>year'},tagger=tagger,doPreprocessing=1,ignoreSingleSentences=1):
    '''
    This funciton is the "wrapper" function for our analysis. The other functions can be used in other analysis. This one is more "niched" to our dataset
    Loads data, does preprocessing, calculates language metrics, calculates readability, creates new table, saves
    VARIABLES IN:
    - path: 'Path/To/Text/Files/eLife.json' (with filename!)
    - spath: 'Path/To/Save/Files/lang.json' (with filename!)
    - tagger: = treetaggerwrapper.TreeTagger(TAGLANG='en')
    - textType: what text is called in the input json. 'body' or 'abstracttext'
    - columnList: Additional columns you want in the data. These should be in the input file. If, for some reason, you want the output to be different, add a <> between. E.g. pubdate_year*year will take "pubdate_year" from input json and export as p"year" in output json.
    - doPreprocessing: 1 for preprocessing. 0 for no preprocessing.
    '''

    columnListDefault = {'strippedText','wordLength','wordCount','sentenceCount','sylCount','flesch','NDC','PercDiffWord','DiffWord_lst'}

    columnList = columnList.difference(columnListDefault)
    columnListIn=[re.split('<>',n)[0] for n in columnList]
    columnListOut=[re.split('<>',n)[-1] for n in columnList]

    columnList=set(columnListOut).union(columnListDefault)

    data = pd.read_json(path)
    data.sort_index(inplace=True)
    data.replace('', np.nan, inplace=True)
    data = data.ix[data[textType].dropna().index] #Drop nan rows

    lang = pd.DataFrame(index=data.index,columns=columnList)

    for n in data.index:
        keepAbstract = qc.identify_badabstracts(data[textType][n])
        if keepAbstract == 1: #This filters out any abstracts where the abstract is "no abstract" or includes "ABSTRACT TRUNCATED"
            if doPreprocessing==1:
                text = lang_prepropipeline(data[textType][n],tagger)
            elif doPreprocessing==0:
                text = lang_minimalprepropipeline(data[textType][n])
            #Calculate the length of each word, sentence and syllable count
            wc, sc, sylCount, remainingText, wordLen = countWordsSentSyl(text,ignoreSingleSentences=ignoreSingleSentences)
            remainingText = ' '.join(remainingText)
            remainingText=remainingText.lower()
            #Only carry on if sentance count is greater than 0
            if wc>0 and sc>0:
                #Calc Flesh and NDC
                fre=FRE(wc,sc,sylCount)
                ndc=NDC(remainingText, wc, sc)   #calc NDC Index and Perctage Diff Words                                         #calc NDC index


                #Insert into table
                lang.flesch[n]=fre
                lang.NDC[n]=ndc[0]
                lang.PercDiffWord[n]=ndc[1]
                lang.DiffWord_lst[n]=ndc[2]
                lang.sylCount[n]=sylCount
                lang.wordLength[n]=wordLen
                lang.sentenceCount[n]=sc
                lang.wordCount[n]=wc
                lang.strippedText[n]=remainingText

                #Insert user specified info into output table
                for v in range(0,len(columnListOut)):
                    lang[columnListOut[v]][n] = data[columnListIn[v]][n]

    #Save file or return lang pandas
    if spath == []:
        return lang
    else:
        lang.to_json(spath)
