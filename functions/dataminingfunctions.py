# Note that scrapers can become obsolete and some changes may be needed to this over time.

#contents
# - get_pubmeddata - gets pubmed data, run with no parameters for interactive, or add parameters
# - txt2dataframe - takes beautifulsoup object and makes dataframe

# This code is a little non-pythonic and, if I was to make it today, it would be restructured a bit.

import codecs
from unidecode import unidecode
#Import packages needed
from Bio import Entrez
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import os
import time
import lxml


def txt2dataframe(datIn,termsIn,dfId='article',filepath='',write=1,include_articleID=1,indexstart=0):

    """
    Creates dataframe from terms. Terms must be hasttags in xml data or "trees" of
    hashtags, for example pubdate-year finds <pubdate>, then <year>
    termsIn can be a preformated list (0th should be articleId) or a collection of tags which  become columes. E.g. 'authorlist,abstracttext' = two columns
    dfId is the id of the dataframe (generally article, but could be author)
    datIn can either be string (filename) or BeautifulSoup class.
    filepath - where to save (only needed if write=1)
    write=1, saves to disk, otherwise returns toinclude_articleID - includes the article id as a column in the dataframe
    include_articleID - only relevant if dfId is not article, include articleID as a columne
    indexstart - what the starting index of the column should be. Useful if extracting pubmed in batches to keep an increasing ID across batches.

    """
    #Check whether datIn needs to be loaded or is BeautifulSoup
    if type(datIn) is str:
        loaddata = open(filepath + '/' + datIn)
        pubMedXMLData=BeautifulSoup(loaddata,'lxml')
    elif type(datIn) is BeautifulSoup:
        pubMedXMLData=datIn
    else:
        print('Data must either be stored in filepath + datIn or datIn = data')
        return
    #From inpue, create a list of terms, add dfId + dfId as 0th term, if string
    if type(termsIn) is list:
        terms=termsIn
    elif type(termsIn) is str:
        terms = sorted(set(re.findall('[^,]*',termsIn)))
        terms[0] = dfId + 'ID' #0th is '', add dfId name
    #Loaded data is in a txt file (string), remake to BeautifulSoup Object
    #If the index is article or the index is not required
    if dfId=='article' or include_articleID==0:
        idData=pubMedXMLData.find_all('pubmed' + dfId)
        id_ind=indexstart
        dataOut = pd.DataFrame(index=np.arange(id_ind, id_ind+len(idData)),columns=terms)
        for item in idData:
            dataOut[terms[0]][id_ind]=id_ind
            for termid in range(1,len(terms)): #Start at 1 due to first term being article dfId, already accounted for
                item_tmp = item
                term_tree = re.findall('[^_]*',terms[termid]) #Get heirarchy by seperating the _
                term_tree = term_tree[0:len(term_tree):2] #Fix spacing
                term_tmp = term_tree[-1] #if single stays the same, if multiple takes last term
                #If term is a multiple tags (e.g. pubdate>year), wittle down item through the terms
                if len(term_tree)!=1:
                    for term_tree_id in range(0,len(term_tree)-1):
                        item_tmp=item_tmp.findChildren(term_tree[term_tree_id])[0] #IMPORTANT, can only take first term of final term in term-tree
                try:
                    texttmp=item_tmp.findAll(term_tmp)
                    textFromBS=''
                    if terms[termid]=='pmid':
                        l=1
                    else:
                        l=len(texttmp)
                    for n in range(0,l):
                        textFromBS=textFromBS+(unidecode(codecs.decode(codecs.encode(str(texttmp[n]),'latin9'),'utf8')))
                        #This adds a space after texts
                        if l>1 and terms[termid]=='abstracttext':
                            textFromBS = textFromBS + ' '
                    textFromBS=re.sub('<[^>]*>','',textFromBS)
            #        textFromBS=re.sub('^[','',textFromBS)
            #        textFromBS=re.sub(']$','',textFromBS)
            #        textFromBS=textFromBS.replace('</' + term_tmp + '>','')
#QC This seperately
                #    textFromBS=textFromBS.replace('VIDEO ABSTRACT.','') #something that can exist in neuron articles
                #    textFromBS=textFromBS.replace('(PsycINFO Database Record','') #something that can exist in later psychological bullitin articles
                except:
                    textFromBS=np.nan
                try:
                    dataOut[terms[termid]][id_ind]=int(textFromBS)
                except:
                    dataOut[terms[termid]][id_ind]=textFromBS
                try:
                    dataOut[terms[termid]][id_ind]=dataOut[terms[termid]][id_ind].astype(float)
                except:
                    pass
            id_ind=id_ind+1
    else:
        #If articleID is wanted but the index is a non-article term.
        articleData=pubMedXMLData.find_all('pubmedarticle')
        article_ind=0
        idDataall=pubMedXMLData.find_all(dfId) #Get number of instances of non-article index
        id_ind=indexstart
        dataOut = pd.DataFrame(index=np.arange(id_ind, id_ind+len(idDataall)),columns=['articleID'] + ['pmid'] + terms)
        for articleItem in articleData:
            idData=articleItem.find_all(dfId)
            pmid=articleItem.findAll('pmid')
            pmid=re.sub('<[^>]*>','',str(pmid[0]))
            for item in idData:
                dataOut['articleID'][id_ind]=article_ind
                dataOut['pmid'][id_ind]=pmid
                #dataOut['pmid'][id_ind]=(unidecode(codecs.decode(codecs.encode(str(texttmp[0]),'latin9'),'utf8')))
                dataOut[terms[0]][id_ind]=id_ind
                for termid in range(1,len(terms)): #Start at 1 due to first term being article dfId, already accounted for
                    item_tmp = item
                    term_tree = re.findall('[^_]*',terms[termid]) #Get heirarchy free
                    term_tree = term_tree[0:len(term_tree):2] #Fix spacing
                    term_tmp = term_tree[-1] #if single stays the same, if multiple takes last term
                    #If term is a multiple tags (e.g. pubdate-year), wittle down item through the terms
                    if len(term_tree)!=1:
                        for term_tree_id in range(0,len(term_tree)-1):
                            item_tmp=item_tmp.findChildren(term_tree[term_tree_id])[0] #IMPORTANT, can only take first term of final term in term-tree
                    try:
                        texttmp=item_tmp.findAll(term_tmp)
                        textFromBS=''
                        if terms[termid]=='pmid':
                            l=1
                        else:
                            l=len(texttmp)
                        for n in range(0,l):
                            textFromBS=textFromBS+(unidecode(codecs.decode(codecs.encode(str(texttmp[n]),'latin9'),'utf8')))
                            if l>1 and terms[termid]=='abstracttext':
                                textFromBS = textFromBS + ' '
                        textFromBS=re.sub('<[^>]*>','',textFromBS)
                        #textFromBS=re.sub('<[^>]*>','',textFromBS)
                        ##textFromBS=re.sub('^[','',textFromBS)
                        #textFromBS=re.sub(']$','',textFromBS)
                        #textFromBS=textFromBS.replace('</' + term_tmp + '>','')
                        #textFromBS=textFromBS.replace('VIDEO ABSTRACT.','') #something that can exist in neuron articles
                    except:
                        textFromBS=np.nan
                    try:
                        dataOut[terms[termid]][id_ind]=int(textFromBS)
                    except:
                        dataOut[terms[termid]][id_ind]=textFromBS
                    try:
                        dataOut[terms[termid]][id_ind]=dataOut[terms[termid]][id_ind].astype(float)
                    except:
                        pass
                id_ind=id_ind+1
            article_ind=article_ind+1
    #Fix directroy for output
    if write==1:
        newDir =filepath+'/'+termsIn.replace(',','_')
        try:
            os.mkdir(newDir) #make directory if missing
        except:
            print('error making new file: ' + newDir + '. May already exist.')
        newDir = newDir + '/id_' + dfId
        try:
            os.mkdir(newDir) #make directory if missing
        except:
            print('error making new file: ' + newDir + '. May already exist.')
        newdatIn = newDir + '/searchresults'
        dataOut.to_json(newdatIn)
    else:
        return dataOut

def get_pubmeddata(searchString=None, dataOfInterest=None, dfId=None, email_address=None, iftxtexists=None):

    """

    Version 2
    Run in wrapper/main
    call with no specified inputs for interactive version in console.


    Code extracts pubmed XML data.
    Loops through and gets all hits for a given searchterm.
    Can either get everything in bulk (all xml) as txt or specfic fields as a dataframe

    searchString -    pubmed search term. e.g. 'thompson[author] & datamining[mesh]'
    dataOfInterest -  specify as 'all' if .txt is wanted. Otherwise, specify columns for dataframe
                       these columns should be tags in the XML pubmeddata.
                       if a tag appears more than once (e.g.) year. A "term tree" can be made.
                       the term tree should be of the structure parent_child (any number of parents is allowed)
                       this means pubdate>year gets the year tag within pubdate.
                       Multiuple data is allowed. Seperated by ,.
                       EXAMPLE: 'abstracttext,pubdate>year,journal>title'
    dfId -           dataframe ID. Only needed if using dataframes. Specifies the ID column of your data (this does not need to be sepecified in the dataOfInterest).
                       This column is usually 'article' or 'author' and the dataframe will use this tag as its index
    email_address     Provide email address for pubmed search
    iftxtexists -     If txt file already exists. Options
                       - '' - prompts user if duplicate detected
                       - 'use'     - use text file
                       - 'update'  - update text file (not implemented yet)
                       - 'ignore'  - ignores txt file.

    Make a file structure of ./data/abstracts/$PUBMED_SEARCHTERM/searchresults.txt - for txt
    Make a file structure of ./data/abstracts/$ID_term/$PUBMED_SEARCHTERM/$COLUMN1_COLUMN2/searchresults for dataframe

    Not the most pythonic code - sorry

    IMPORTANT - SINCE ORIGINALLY USING THIS CODE. PUBMED AND EFETCH HAS CHANGED.
    IF ERRORS KEEP OCCURING WHEN QUERYING PUBMED, CHANGE maxPubmedSearchReturn IN CODE TO 200.

    """

    # Set defaults
    if searchString == None:
        searchString = ''

    if dataOfInterest == None:
        dataOfInterest = ''

    if dfId == '':
        dfId=''

    if email_address == None:
        email_address = ''

    if iftxtexists == None:
        iftxtexists = ''

    #Query for searchString and parameters
    #Query for search term when run
    if searchString == '':
        searchString = input("Search pubmed with: \n -->")
    #Query to export as txt or datafram (by specifying columns/tags)
    #Query for search term when run
    if dataOfInterest == '':
        dataOfInterest = input("For an output of txt of everything, leave blank (or 'all'). \n For dataframe, type htmlterms seperated by comma e.g. AbstractText,PubDate \n IMPORTANT: keeps nested terms as well (i,e, 'article' will include 'title')). \n Possible to specify tree of tags with _ by pubdate_year which will find year within pubdate tag \n ID column is specified in next step (default article. Author is also possible). \n possible tags: abstracttext, articletitle, authorlist, pubdate_year, pmid, journal: \n -->")




    # PARAMETERS
    workingDirectory = os.getcwd()
    maxPubmedSearchReturn = 200 #The largest amount of files that can be returned (max is 10000).
    if email_address == '':
        email_address = input('Provide email address for pubmed identifier:')

    #SETUP: INPUT
    #Term yuou want to search in pubmed
    #searchString='clinical neuroscience[Affiliation] & Karolinska[Affiliation]'
    if dataOfInterest == ('all') or dataOfInterest == '':
        output = 'txt'
    else:
        output = 'df'
        if dfId == '':
            dfId = input("ID column in dataframe (usually article or author. Leave blank for article). \n --- multiple IDs are possible, seperated by comma (but not really useful). \n --- IDs must be parents of seearch term (i.e. if ID is author, the search terms must be within the author tag (e.g. affiliation, not: title))\n -->") #Query for search term when run
        if dfId == '':
            dfId = 'article'
        #From inpue, create a list of terms, add articleID as 0th term
        terms = sorted(set(re.findall('[^,]*', dataOfInterest)))
        terms[0] = dfId + 'ID' #0th is '', add articleID name
        dfId = sorted(set(re.findall('[^,]*', dfId)))
        dfId = dfId[1:] #remove blank term
    #SETUP: FILE STRUCTURE
    #Where to save files and create file structure
    try:
        os.mkdir(workingDirectory + '/data/')
        os.mkdir(workingDirectory + '/data/abstracts//')
    except:
        pass
    filename_pubMedData = workingDirectory + '/data/abstracts/' + searchString + '/'
    filename_pubMedData=filename_pubMedData.replace(' ','_') #Make pretty filename
    filename_pubMedData=filename_pubMedData.replace('\"','') #Make pretty filename
    try:
        os.mkdir(filename_pubMedData) #make directory if missing
    except:
        pass
    #Check to see whether a txt file already exists for search term
    if os.path.isfile(filename_pubMedData + '/searchresults.txt')==True:
        file = open(filename_pubMedData + '/searchresults.txt','a+')
        print('\nNOTE: txt file for serchterm already exists\n')
        if iftxtexists == '':
            iftxtexists=input('use or ignore?')
        if iftxtexists == 'use':
            txt_fileuse = 1
            txt_filepath = filename_pubMedData + '/searchresults.txt'
        else:
            txt_fileuse = 0
    else:
        txt_fileuse = 0


    if output=='txt':
        filename_pubMedData = filename_pubMedData + '/searchresults.txt'
        file = open(filename_pubMedData,'w') #Create output file
    else:
        #Create filestructure ~/data/abstracts/SEARCHTERM/ID_xxx/COLUMNS
        filename_pubMedData_tmp=[]
        for n in range(0,len(dfId)):
            filename_pubMedData_tmp.append(filename_pubMedData+'/id_' + dfId[n])
            try:
                os.mkdir(filename_pubMedData_tmp[n]) #make directory if missing
            except:
                pass
            filename_pubMedData_tmp[n]=filename_pubMedData_tmp[n]+'/'+ dataOfInterest.replace(',','_')
            try:
                os.mkdir(filename_pubMedData_tmp[n]) #make directory if missing
            except:
                pass
            filename_pubMedData_tmp[n]=filename_pubMedData_tmp[n]+'/searchresults'
        filename_pubMedData=filename_pubMedData_tmp


    #QUERY PUBMED
    i=0 # Loop number
    #Only query if the txt file is not already on computer
    if txt_fileuse == 0:
        #Set email addrress
        Entrez.email = email_address
        #Search Pubmed for stuff  and get the pubmedids
        stopwhile=0 # Exit parameter
        start=0 #Pubmed Start ind
        while stopwhile==0:
            hdl = Entrez.esearch(db='pubmed', retstart=start, retmax=maxPubmedSearchReturn,retmode='xml',term=searchString,id='ids')
            results = Entrez.read(hdl) #make the object readible (and not and evil hack object)
            pubmedid=results['IdList'] #These are the pubmed IDs that match your search term

            #Fetch the xml information based on pubmedid
            er=0
            erind=0
            erind2=0
            #At times pubmed servers can be unstable. Rerun if an error occurs.
            while er==0:
                try:
                    hdl = Entrez.efetch(db='pubmed',retmode='xml',id=pubmedid)
                    #BeautifulSoupy the object
                    pubMedXMLData=BeautifulSoup(hdl,'lxml')
                    er=1
                except:
                    er=0
                    erind=erind+1
                    time.sleep(10) #Wait ten seconds for safety
                    pubMedXMLData=[]
                    print('Pubmed Download Error (call error), rerunning. Failed ' + str(erind) + ' times.')
                if er==1:
                    idData=pubMedXMLData.find_all('pubmedarticle')
                    if len(idData)!=len(pubmedid):
                        erind2=erind2+1
                        er=0
                        time.sleep(10) #Wait ten seconds for safety
                        pubMedXMLData=[]
                        idData=[]
                        print('Pubmed Download Error (articles missing, ' + str(len(idData)) + ' vs ' + str(len(pubmedid)) + '): rerunning. Failed ' + str(erind2) + ' times.')
            if i==0 and len(pubmedid)<maxPubmedSearchReturn:
                print('Downloaded ' + str(len(pubmedid)) + ' articles')
            else:
                print('Downloaded batch ' + str(i) + ' containing ' + str(len(pubmedid)) + ' articles')

            if output=='txt':  #save everything in to text
            #Save XML data as text file for use another day
                file.write(str(pubMedXMLData)) #File has to be saved as a string (for txt which I think is the most efficient way to store this file
            else:   #save keyterm into pandas
                #Start by parcing the XML by articles
                #Loop over number of indexes specified
                for n in range(0,len(dfId)):
                    #tet2dataframe creates datafram from terms with index dfId
                    dataOut=txt2dataframe(pubMedXMLData,terms,dfId[n],'',0,1,start)
                    #Save dataframe as json if dataframe, txt if all -  prints feedback
                    if i==0 and len(pubmedid)<maxPubmedSearchReturn:
                        #dataOut.to_json(filename_pubMedData[n])
                        dataOut.to_json(filename_pubMedData[n])
                        print('Saved as pandas dataframe with id:' + dfId[n] + ' (format: json)')
                    else:
                        #dataOut.to_json(filename_pubMedData[n] + '_batch' + str(i))
                        dataOut.to_json(filename_pubMedData[n] + '_batch' + str(i))
                        print('Saved file  batch ' + str(i) + ' as pandas dataframe with id:' + dfId[n] + ' (format: json)')
            if len(pubmedid)<maxPubmedSearchReturn: # Exit forloop
                if output=='txt': #cleanup txt file, if printing to txtfile
                    print('Saved as txt file')
                    file.close()
                stopwhile=1
            else:
                start=start+maxPubmedSearchReturn #Update start index, for next loop
            i=i+1 #Update loop index
            time.sleep(1) #Wait a seconds for safety

    elif txt_fileuse == 1 and  output=='df':
        print('---Using txtfile to create dataframe\n')
        for n in range(0,len(dfId)):
        #tet2dataframe creates datafram from terms with index dfId
            dataOut=txt2dataframe(txt_filepath,terms,dfId[n],'',0,1)
            #dataOut.to_json(filename_pubMedData[n])
            #print(dataOut)
            dataOut.to_json(filename_pubMedData[n])
            print('Saved as pandas dataframe with id:' + dfId[n] + ' (format: json)')

    #Merge the batch files and cleanup if pubmed searches > 10000 and pckle
    if i>1 and output=='df':
        for pfn in range(0,len(filename_pubMedData)):
            print('Combining batch files')
            p=pd.read_json(filename_pubMedData[pfn] + '_batch' + str(0))
            for n in range(1,i):
                p2=pd.read_json(filename_pubMedData[pfn] + '_batch' + str(n))
                p=pd.concat([p,p2])
            print('Saving concatinated file (format: json)')
            p.reset_index(inplace=True)
            p.to_json(filename_pubMedData[pfn])
            print('Cleaning up batch files')
            for n in range(0,i):
                cmd = filename_pubMedData[pfn] + '_batch' + str(n) #This may only work on unix
                os.remove(cmd)









#Sometimes <pubdate><year> is <medlinedate> instead. Search missing year pmids again and get medlinedate (a little bit of a bandage, but gets years for several 1000 articles.)
def get_medlineyear(pmid):
    Entrez.email = 'william.thompson@ki.se'
    hdl = Entrez.efetch(db='pubmed',retmode='xml',id=pmid)
    #BeautifulSoupy the object
    pubMedXMLData=BeautifulSoup(hdl,'lxml')
    articleData=pubMedXMLData.find_all('pubmedarticle')
    year = []
    for articleItem in articleData:
        yearData=articleItem.find_all('medlinedate')
        #print(yearData)
        year.append(int(str(yearData[0])[13:17]))
    return year
