#%%
#md

"""
This script downloads the dataset use in the analysis.

__It requires 2 inputs to be specified__

repo_directory and email (see first cell block).
"""

#%%

# Where is the main directory of the repo
repo_directory = './'
# Pubmed requires you to identify with an email addreesss
email = ''

#%%
import os
os.chdir(repo_directory)

import numpy as np
import pandas as pd
import functions.dataminingfunctions as dmf
import functions.readabilityFunctions as rf



#%%

#Load journal info
journalInfo=pd.read_csv('./JournalSelection/JournalSelection.csv')


#%%
#md

"""
Specify the search data that you want to get from pubmeddata
"""

#%%

#What to get. "all" saves a txt. Otherwise the xml tags wanted (see https://www.nlm.nih.gov/bsd/licensee/elements_alphabetical.html). Seperated by a comma
#"Trees" are possible to specify column you want. (e.g. <year> occurs) in several
#places so pubate_year takes the <year> tag in <pubdate>
dataOfInterest = 'abstracttext,pubdate_year,pmid,articletitle,journal_title,keyword,doi'
#If dataframe, what is the index column (usally article or author)
dfId = 'article'

#%%
#md

"""
Download the data
"""

#%%

for n in range(0, len(journalInfo)):
    #Parameters needed (if left blank, get_pubmeddata asks for response)
    #What to search pubmed with
    searchString = journalInfo.search[n]
    print(' ---Running search: ' + searchString + ' (' + str(n) + ')' + ' ---')

    #Run get data
    dmf.get_pubmeddata(searchString.lower(), dataOfInterest, dfId, email, 'ignore')

#%%
#md

"""
Sometimes the pubdate, year tags were missing in articles. The next cell finds those instances and
"""

#%%

# Sometimes the
for n in range(0, len(journalInfo)):
    searchString = journalInfo.search[n].lower()
    #make path to data (always this, if dataframe)
    mDir = os.getcwd() + '/data/abstracts/' + searchString + '/' + 'id_' + dfId + '/' + dataOfInterest + '/'
    mDir = mDir.replace(' ','_')
    mDir = mDir.replace(',','_')
    mDir = mDir.replace('\"','')
    dat=pd.read_json(mDir + 'searchresults')
    dat.sort_index(inplace=True)
    idMissing = [i for i,x in enumerate(dat.pubdate_year) if x == '']
    if len(idMissing)>0:
        #Make a list of strings
        pmidMissing=list(map(str,list(dat.pmid[idMissing])))
        print(' ---Finding missing years (' + str(len(pmidMissing)) + ' found): ' + searchString + '. term: ' + str(n) + ' ---')
        missingYears = dmf.get_medlineyear(list(pmidMissing))
        dat['pubdate_year'].loc[idMissing]=missingYears
        dat.to_json(mDir + 'searchresults')



#%%
#md

"""
For the "nr authors" the author info also has to be download.
"""

#%%

#What to get. "all" saves a txt. Otherwise the xml tags wanted (see https://www.nlm.nih.gov/bsd/licensee/elements_alphabetical.html). Seperated by a comma
#"Trees" are possible to specify column you want. (e.g. <year> occurs) in several
#places so pubate_year takes the <year> tag in <pubdate>
dataOfInterest = 'forename,lastname,affiliation'
#If dataframe, what is the index column (usally article or author)
dfId = 'author'

for n in range(0, len(journalInfo)):
    #Parameters needed (if left blank, get_pubmeddata asks for response)
    #What to search pubmed with
    searchString = journalInfo.search[n]
    print(' ---Running search: ' + searchString + ' (' + str(n) + ')' + ' ---')
    #Run get data
    dmf.get_pubmeddata(searchString.lower(), dataOfInterest, dfId, email, 'ignore')
    #dataOfInterest = 'forename,lastname,affiliation'
    #dfId = 'author'
    #dmf.get_pubmeddata(searchString.lower(),dataOfInterest,dfId,email,'ignore')
