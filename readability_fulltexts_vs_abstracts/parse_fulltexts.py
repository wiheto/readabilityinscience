import re
import unidecode
import pandas as pd
import numpy as np
import os
import io
import datetime
import math


def parse_bmc(basePath, outPath):
    """
    Parsing fulltext articles from BMC Biology.

    Reads in fulltext .txts and extracts fulltext body and abstract as well as doi

    Output: JSON pandas dataframe in output directory plus csv containing article types extracted

    """

    journalList = ["BMC_Biol"]

    # Regex for abstract and body
    # Checkline regex
    tabpat = re.compile("\t")

    abstrpat = re.compile("(?:provided the original work is properly cited\.|.*provided this notice is preserved along with the article's original URL\.|applies to the data made available in this article, unless otherwise stated\.)")

    bodypat = re.compile('^(.*?)==== Body\n')

    endpat = re.compile('^([Ss]upplementary [Ii]nformation|[Ss]upplementary [Mm]aterial|[Ss]upporting [Ii]nformation|Abbreviations|Availability of supporting data|Authors\' contributions|Author contributions|Acknowledgements|Patient Summary|==== Refs)\n')

    for j in range(0, len(journalList)):
        print("Parsing text files from journal " + journalList[j])
        # Get list of files
        fileList = []

        for file in os.listdir(basePath + journalList[j]):
            if file.endswith(".txt"):
                fileList.append(file)


        overall_list = []

        for i in range(0, len(fileList)):

            with io.open(basePath + journalList[j] + '/' + fileList[i], 'r', encoding='utf8') as file:
                output = []
                abstrpats = []
                bodypats = []
                endpats = []
                k = 0
                for line in file: # read line by line
                    if re.search(tabpat, line) is None:
                        output.append(line)
                    else:
                        output.append('\n')
                    if re.search(abstrpat, line) is not None:
                        abstrpats.append(k)
                    if re.search(bodypat, line) is not None:
                        bodypats.append(k)
                    if re.search(endpat, line) is not None:
                        endpats.append(k)
                    k += 1

            try:
                abstract = unidecode.unidecode(' '.join(output[max(abstrpats)+1 : min(bodypats)]).replace('\n',' '))
            except:
                abstract = np.nan

            try:
                if(len(endpats)) > 0:
                    body = unidecode.unidecode(' '.join(output[max(bodypats)+1 : min(endpats)]).replace('\n',' '))
                else:
                    body = unidecode.unidecode(' '.join(output[max(bodypats)+1 : ]).replace('\n',' '))
            except:
                body = np.nan

            try:
                bodystop = unidecode.unidecode(' '.join(output[min(endpats): ] ).replace('\n',' '))
            except:
                bodystop = np.nan

            try:
                prebody = unidecode.unidecode(' '.join(output[0 : min(abstrpats + bodypats)+1]).replace('\n',' '))
            except:
                prebody = np.nan

            txtfile = fileList[i] # save name of textfile for easier QC later on

            # Extract year from filename
            year = re.search("_([0-9]{4})_", txtfile).group(1)

            print("Parsing file " + fileList[i] + " from journal " + journalList[j] + ', ' + str(len(fileList) - i) + " files left for that journal")

            # doi pattern from http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
            try:
                 doi = re.search("(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+)", prebody).group(1)
                 doi = re.sub("[^\d]+$", '', doi) # remove anything from the end of the doi if it ends with a string
                 fulldoi = doi

            except:
                 doi = np.nan

            try:
                pmid_regex = re.escape(re.search("\/(.*)", doi).group(1)) + "(\d+)10\." # This uses the previously extracted doi to look for the pmid
            except:
                pmid_regex = np.nan

            try:
                 pmid = int(re.search(pmid_regex, prebody).group(1)) # group 1 because that is being output to (\d+)
            except:
                 pmid = np.nan

            article_type_regex = '(Anniversary [Uu]pdate?|Commentary?|Comment?|Correction?|Correspondence?|Editorial?|Focus?|Forum?|Interview?|Opinion?|Question and Answer?|Q&A?|Review?|[Rr]esearch [Aa]rticle?|Methodology?|Software?)'

            typepat = re.compile(article_type_regex)
            try:
                articletype = re.search(typepat, prebody).group(1)
            except:
                try:
                    article_type_regex = re.escape(str(fulldoi)) + '(Anniversary update?|Best Practice?|Book Reviews?|Case Report?|Collection?|Commentary?|Comment?|Community Page?|Correction?|Correspondence?|Editorial?|Education?|Essay?|Feature?|Focus?|Formal Comment?|Forum?|Guidelines and Guidance?|Health in Action?|Historical and Philosophical Perspectives?|Interview?|Journal Club?|Learning Forum?|Message from PLoS?|Message from the Founders?|Message from the PLoS Founders?|Meta-Research?|Methodology?|Neglected Diseases?|Obituary?|Online Only?|Online Quiz?|Opinion?|Perspectives?|Policy?|Primer?|Q&A?|Review?|Research Article?|Research in Translation?|Retraction?|Software?|Student Forum?|Synopsis?|Unsolved Myster.?|The PLoS Medicine Debate?)'
                    typepat = re.compile(article_type_regex)
                    articletype = re.search(typepat, prebody).group(1)
                except:
                    articletype = np.nan

            overall_list.append((abstract, body, bodystop, year, doi, pmid, txtfile, prebody, articletype))

        print("Making data frame")
        df_overall = pd.DataFrame(overall_list, columns = ['abstract', 'body', 'bodystop', 'year', 'doi', 'pmid', 'txtfile', 'prebody', 'articletype'])
        df_overall['journal'] = journalList[j]

        df_overall.to_json(outPath + journalList[j] + '.json')

        articletypes = pd.Series(df_overall.groupby('articletype').count().journal)
        articletypes.sort_values(inplace=True, ascending=False)
        articletypes.to_csv(outPath + journalList[j] + '_FreqArticleType.csv')


def parse_elife(basePath, outPath):
    """
    Parsing fulltext articles from eLife.

    Reads in fulltext .txts and extracts fulltext body and abstract as well as doi

    Output: JSON pandas dataframe in output directory plus csv containing article types extracted

    """

    journalList = ['eLife']

    # Regex for abstract and body start and stop points

    abstractstart = re.compile("which permits unrestricted use and redistribution provided that the original author and source are credited.")
    abstractstart2 = re.compile("Creative Commons CC0 public domain dedication.")
    abstractstop1 = re.compile("Author[\s-]Keywords")
    abstractstop2 = re.compile("Author[\s-]keywords")
    abstractstop3 = re.compile("DOI: http://dx.doi.org/10.")

    bodyStart = re.compile("^==== Body|==== Body\s?Introduction")
    bodyStop = re.compile("==== Body Supporting Information|^Funding [Ii]nformation|^Acknowledgements?|^Ethics|^Additional [Ii]nformation|^Competing interests?:?|^==== Refs")


    for j in range(0,len(journalList)):  # loop through multiple journals
        print("Parsing text files from journal " + journalList[j])
        # Get list of files
        fileList = []
        for file in os.listdir(basePath + journalList[j]):
            if file.endswith(".txt"):
                fileList.append(file)

        overall_list = []
        for i in range(0, len(fileList)):  # loop through the fulltexts files
            with io.open(basePath + journalList[j] + '/' + fileList[i], 'r', encoding='utf8') as f:

                output = f.read()
                # Extract year from filename
                try:
                    year = re.search("_([0-9]{4})_", fileList[i]).group(1)
                # Extract from textfile:
                except:
                    loc=output.find(fileList[i][8:14])
                    after=output[loc+8:loc+20]
                    before=output[loc-20:loc]
                    try:
                        match = re.search(r'\d{4}', after).group()
                    except:
                        match = re.search(r'\d{4}', before).group()
                    for y in range(2012,int(datetime.date.today().year+1)):
                        if re.match(str(y),match):
                            year=str(y)
                            break
                        else:
                            year='unkown'

                # doi pattern from http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
                try:
                    doi = re.search("(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+)", output).group(1)
                    doi = re.sub("[^\d]+$", '', doi)  # remove anything from the end of the doi if it ends with a string

                except:
                    doi = np.nan
                    continue

                try:
                    pmid_regex = re.compile('\d{4,}'+re.escape(doi))
                    pmidstring=re.search(pmid_regex, output).group(0)
                    pmid = pmidstring[0:len(pmidstring)-len(doi)]
                except:
                    pmid = np.nan

                #extract article type from text file
                try:
                    eLifeNr=doi[len(doi)-11:len(doi)+1]
                    eLifePattern=re.compile(eLifeNr)
                    ArticleTypeStart=re.search(eLifePattern,output).end()
                    string=output[ArticleTypeStart:ArticleTypeStart+30]
                    ArticleType=re.findall('[A-Z][^A-Z]*',string)  # Find article type
                    ArticleType=ArticleType[0]
                except:
                    ArticleType=np.nan

                tabfinder=re.compile("\t")
                outputSplit=output.splitlines()
                outputNew=[]
                for line in outputSplit:
                    try:
                        re.search(tabfinder,line).end()
                    except:
                        outputNew.append(line)

                outputNew2=outputNew[0:4]
                exluder1=re.compile("^DOI:$")
                exluder2=re.compile("^http://dx.doi.org/")
                for thing in outputNew[4:]:   # skip over the first 3 paragraphs/lines
                    try:
                        re.search(exluder1).start()
                    except:
                        try:
                            re.search(exluder2).start()
                        except:
                            outputNew2.append(thing)


                output_joined = unidecode.unidecode(''.join(outputNew2).replace('\n',' '))

                #Get start and stop of abstract
                try:
                    abstractStartPoint = re.search(abstractstart,output_joined).end()
                except:
                    try:
                        abstractStartPoint = re.search(abstractstart2,output_joined).end()
                    except:
                        abstractText=np.nan
                try:
                    abstractStopPoint1 = re.search(abstractstop1, output_joined).start()
                except:
                    abstractStopPoint1 = np.nan
                try:
                    abstractStopPoint2 = re.search(abstractstop2, output_joined).start()
                except:
                    abstractStopPoint2 = np.nan
                try:
                    abstractStopPoint3 = re.search(abstractstop3, output_joined).start()
                except:
                    abstractStopPoint3 = np.nan
                try:
                    lst=[abstractStopPoint1,abstractStopPoint2,abstractStopPoint3]
                    nlst=[]
                    for s in lst:
                        if isinstance( s, int ):
                            nlst.append(s)
                    abstractStopPoint=min(nlst)
                    abstractText = output_joined[abstractStartPoint:abstractStopPoint]
                except:
                    abstractText = np.nan

                # Extract body of text
                startP=[]
                for idx,line in zip(range(len(outputNew2)),outputNew2):
                    try:
                        if re.search(bodyStart,line)!=None:
                            startP.append(idx)
                    except:
                        pass
                stopP=[]
                ID=[]
                for idxx, line in zip(range(len(outputNew2)),outputNew2):  # save line when finding pattern
                    try:
                        if re.search(bodyStop,line)!=None:
                            ID.append(re.search(bodyStop,line).group())
                            stopP.append(idxx)
                    except:
                        pass
                try:
                    outputNew3=outputNew2[min(startP)+1:min(stopP)]
                    indx=stopP.index(min(stopP))
                    bodyStopID=ID[indx]
                    bodyText = unidecode.unidecode(''.join(outputNew3).replace('\n',' '))

                except:
                    bodyText=np.nan
                    bodyStopID=np.nan

                overall_list.append((abstractText, bodyText, bodyStopID ,year, doi, pmid, ArticleType))  # double paranthesis makes list into tuple-accepting

        print("Making data frame")
        df_overall = pd.DataFrame(overall_list, columns = ['abstract', 'body','bodyStopId', 'year', 'doi', 'pmid', 'articleType'])
        df_overall['journal'] = journalList[j]

        ArticleTypes=[]
        for i in range(0,len(df_overall.articleType.unique())):  # extract all unique article types for eLife
            print(df_overall.articleType.unique()[i])
            ArticleTypes.append(df_overall.articleType.unique()[i])  # get them into a list
        for art in ArticleTypes:
            print(art)
            print(len(df_overall.abstract[df_overall.articleType == art]))

        df_overall = df_overall[ (df_overall.articleType == 'Research ') | (df_overall.articleType != 'Short ')| (df_overall.articleType != 'Insight')| (df_overall.articleType != 'Feature ')| (df_overall.articleType != 'Editorial')| (df_overall.articleType != 'Registered ')| (df_overall.articleType != 'Tools and ')| (df_overall.articleType != 'Cell ')| (df_overall.articleType != 'Neuroscience')| (df_overall.articleType != 'Biochemistry')]
        df_overall.to_json(outPath + journalList[j] + '.json')

        articletypes = pd.Series(df_overall.groupby('articleType').count().journal)
        articletypes.sort_values(inplace=True, ascending=False)
        articletypes.to_csv(outPath + journalList[j] + '_FreqArticleType.csv')


def parse_genbiol(basePath, outPath):
    """
    Parsing fulltext articles from Genome Biology.

    Reads in fulltext .txts and extracts fulltext body and abstract as well as doi

    Output: JSON pandas dataframe in output directory plus csv containing article types extracted

    """

    journalList = ["Genome_Biol"]

    # Checkline regex
    tabpat = re.compile("\t")

    abstrpat = re.compile("(?:provided the original work is properly cited\.|.*provided this notice is preserved along with the article's original URL\.|applies to the data made available in this article, unless otherwise stated\.|BioMed Central Ltd\.?|Copyright \S+ [0-9]{4,} GenomeBiology.com)")

    bodypat = re.compile('^( ?)==== Body\n')

    endpat = re.compile("^([Ss]upplementary [Ii]nformation|[Ss]upplementary [Mm]aterial?s|Acknowledgement?s|==== Refs|Abbreviation?s|Additional [Ff]iles?|Additional [Dd]ata [Ff]iles?|Data [Aa]ccess|Abbreviations?|Competing interests?|Authors\' contributions)\n")

    abstrpat_lastditch = re.compile('(GenomeBiology.com)(.*?)(GenomeBiology.com)(.*?)(==== Body)')

    abstrchop = re.compile('(.*?)(Electronic [Ss]upplementary [Mm]aterials?)')

    abstr_oneliners = re.compile('(.+BioMed Central Ltd\.?|.+GenomeBiology.com\.?|.+ provided the original work is properly cited.)([A-Z0-9].*?)(==== Body|$)')

    abstr_nothing = re.compile('([0-9]{4,}BioMed Central Ltd|[0-9]{4,}GenomeBiology.com|Conference website:)')


    for j in range(0,len(journalList)):
        print("Parsing text files from journal " + journalList[j])
        # Get list of files
        fileList = []
        for file in os.listdir(basePath + journalList[j]):
            if file.endswith(".txt"):
                fileList.append(file)
        overall_list = []

        for i in range(0, len(fileList)):

            with io.open(basePath + journalList[j] + '/' + fileList[i], 'r', encoding='utf8') as file:#open file
                output = []
                abstrpats = []
                bodypats = []
                endpats = []
                k = 0
                for line in file: # read line by line
                    if re.search(tabpat, line) is None:
                        output.append(line)
                    else:
                        output.append('\n')
                    if re.search(abstrpat, line) is not None:
                        abstrpats.append(k)
                    if re.search(bodypat, line) is not None:
                        bodypats.append(k)
                    if re.search(endpat, line) is not None:
                        endpats.append(k)
                    k = k+1

            try:
                abstract = unidecode.unidecode(' '.join( output[ max(abstrpats)+1 : min(bodypats) ] ).replace('\n',' '))
                if re.search(abstrchop, abstract) is not None:
                    abstract = re.search(abstrchop, abstract).group(1)
            except:
                abstract = 'NaN'

            try:
                if(len(endpats)) > 0:
                    body = unidecode.unidecode(' '.join( output[ max(bodypats)+1 : min(endpats) ] ).replace('\n',' '))
                else:
                    body = unidecode.unidecode(' '.join( output[ max(bodypats)+1 : ] ).replace('\n',' '))
            except:
                body = 'NaN'

            try:
                bodystop = unidecode.unidecode(' '.join( output[ min(endpats): ] ).replace('\n',' '))
            except:
                bodystop = 'NaN'

            try:
                prebody = unidecode.unidecode(' '.join( output[ 0 : min(abstrpats + bodypats)+1 ] ).replace('\n',' '))
            except:
                prebody = 'NaN'

            if len(abstract) == 0 or abstract == 'NaN':
                try:
                    abstract = re.search(abstr_oneliners, prebody).group(2)
                except:
                    pass

            if re.search(abstr_nothing, abstract) is not None:
                abstract = 'NaN'

            txtfile = fileList[i] # save name of textfile for easier QC later on

            # Extract year from filename
            year = re.search("_([0-9]{4})_", txtfile).group(1)

            print("Parsing file " + fileList[i] + " from journal " + journalList[j] + ', ' + str(len(fileList) - i) + " files left for that journal")

            # doi and pmid bollockery
            pmidpat = re.compile('(\d{8})[A-Z]')

            try:
                pmid = int(re.search(pmidpat, prebody).group(1))
            except:
                pmid = 'NaN'

            if pmid == 'NaN':
                gbdoistr = '((gb-(' + year + '|' + str(int(year)+1) + '|' + str(int(year)-1) + ')' + '-\S+?))([A-Z|\'A-Z])'
            else:
                gbdoistr = '(gb-(' + year + '|' + str(int(year)+1) + '|' + str(int(year)-1) + ')' + '-\S+)(\d{8})'
            gbdoipat = re.compile(gbdoistr)

            # doi pattern from http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
            try:
                doi = re.search(gbdoipat, prebody).group(1)
            except:
                try:
                    doi = re.search("(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+?)([A-Z|\'A-Z])", prebody).group(1)
                except:
                    doi = 'NaN'

            articleType_str = '(' + doi + ')' + '(\S*?)' + '([A-Z].*?[a-z])[A-Z|\'A-Z]'
            typepat = re.compile(articleType_str)
            try:
                articletype = re.search(typepat, prebody).group(3)
            except:
                articletype = 'NaN'

                # doi fixing
            if doi != 'NaN':
                doitemp = doi
                if re.search("(10[.][0-9]{4}/.+)", doitemp) is not None:
                    doi = re.search("(10[.][0-9]{4}/.+)", doitemp).group(1)
                    try:
                        pmid = re.search("(\d{8})(10[.][0-9]{4}/.+)", doitemp).group(1)
                    except:
                        pass
                elif doitemp[0:3] == 'gb-' :
                    doi = '10.1186/' + doi

            overall_list.append((abstract, body, bodystop, year, doi, pmid, txtfile, prebody, articletype))

        print("Making data frame")
        df_overall = pd.DataFrame(overall_list, columns = ['abstract', 'body', 'bodystop', 'year', 'doi', 'pmid', 'txtfile', 'prebody', 'articletype'])
        df_overall['journal'] = journalList[j]

        df_overall.to_json(outPath + journalList[j] + '.json')

        articletypes = pd.Series(df_overall.groupby('articletype').count().journal)
        articletypes.sort_values(inplace=True, ascending=False)
        articletypes.to_csv(outPath + journalList[j] + '_FreqArticleType.csv')


def parse_plos(basePath, outPath):
    """
    Parsing fulltext articles from PloS journals PloS Medicine and Biology.

    Reads in fulltext .txts and extracts fulltext body and abstract as well as doi

    Output: JSON pandas dataframe in output directory plus csv containing article types extracted

    """

    journalList = ['PLoS_Med', 'PLoS_Biol']

    # Checkline regex
    tabpat = re.compile('\t')

    abstrpat = re.compile(
        '(?:provided the original work is properly cited|provided this notice is preserved along with the article\'s original URL|provided the original author and source are credited|modified, built upon, or otherwise used by anyone for any lawful purpose)')

    bodypat = re.compile('^(.*?)(==== Body\n|Editor\'s summary\n)')

    endpat = re.compile(
        '^([Ss]upplementary [Ii]nformation|[Ss]upplementary [Mm]aterial|[Ss]upporting [Ii]nformation|Abbreviations|Availability of supporting data|Authors\' contributions|Author contributions|Acknowledgements|Patient Summary|==== Refs)\n')

    for j in range(0, len(journalList)):
        print("Parsing text files from journal " + journalList[j])
        # Get list of files
        fileList = []
        for file in os.listdir(basePath + journalList[j]):
            if file.endswith(".txt"):
                fileList.append(file)

        overall_list = []

        for i in range(0, len(fileList)):

            with io.open(basePath + journalList[j] + '/' + fileList[i], 'r', encoding='utf8') as file:
                output = []
                abstrpats = []
                bodypats = []
                endpats = []
                k = 0
                for line in file:  # read line by line
                    if re.search(tabpat, line) is None:
                        output.append(line)
                    else:
                        output.append('\n')
                    if re.search(abstrpat, line) is not None:
                        abstrpats.append(k)
                    if re.search(bodypat, line) is not None:
                        bodypats.append(k)
                    if re.search(endpat, line) is not None:
                        endpats.append(k)
                    k += 1

                if len(bodypats) > 1:
                    print(str(fileList[i]))

            try:
                abstract = unidecode.unidecode(' '.join(output[max(abstrpats) + 1: min(bodypats)]).replace('\n', ' '))
            except:
                abstract = np.nan

            try:
                if (len(endpats)) > 0:
                    body = unidecode.unidecode(' '.join(output[max(bodypats) + 1: min(endpats)]).replace('\n', ' '))
                else:
                    body = unidecode.unidecode(' '.join(output[max(bodypats) + 1:]).replace('\n', ' '))
            except:
                body = np.nan

            try:
                bodystop = unidecode.unidecode(' '.join(output[min(endpats):]).replace('\n', ' '))
            except:
                bodystop = np.nan

            try:
                prebody = unidecode.unidecode(' '.join(output[0: min(abstrpats + bodypats) + 1]).replace('\n', ' '))
            except:
                prebody = np.nan

            txtfile = fileList[i]  # save name of textfile for easier QC later on

            # Extract year from filename
            year = re.search("_([0-9]{4})_", txtfile).group(1)

            print("Parsing file " + fileList[i] + " from journal " + journalList[j] + ', ' + str(
                len(fileList) - i) + " files left for that journal")

            # doi pattern from http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
            try:
                doi = re.search("(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+)", prebody).group(1)
                doi = re.sub("[^\d]+$", '', doi)  # remove anything from the end of the doi if it ends with a string

                fulldoi = doi
                doi = re.sub("PMEDICINE.*", '',
                             doi)  # Also remove anything starting with PMEDICINE, which obfuscates later dois in PloS Med
                doi = re.sub("PBIOLOGY.*", '',
                             doi)  # Also remove anything starting with PBIOLOGY, which obfuscates later dois in PloS Biol

                doi = re.sub("[0-9]{2}-PLME.*", '', doi)
                doi = re.sub("[0-9]{2}-PLBI.*", '', doi)

                doi = re.sub("plme.*", '', doi)
                doi = re.sub("plbi.*", '', doi)

            except:
                doi = np.nan

            try:
                pmid_regex = re.escape(re.search("\/(.*)", doi).group(
                    1)) + "(\d+)10\."  # This uses the previously extracted doi to look for the pmid
            except:
                pmid_regex = np.nan

            try:
                pmid = int(re.search(pmid_regex, prebody).group(1))  # group 1 because that is being output to (\d+)
            except:
                pmid = np.nan

            article_type_regex = re.escape(str(
                doi)) + '(Anniversary update?|Best Practice?|Book Reviews?|Case Report?|Collection?|Commentary?|Comment?|Community Page?|Correction?|Correspondence?|Editorial?|Education?|Essay?|Feature?|Focus?|Formal Comment?|Forum?|Guidelines and Guidance?|Health in Action?|Historical and Philosophical Perspectives?|Interview?|Journal Club?|Learning Forum?|Message from PLoS?|Message from the Founders?|Message from the PLoS Founders?|Meta-Research?|Methodology?|Neglected Diseases?|Obituary?|Online Only?|Online Quiz?|Opinion?|Perspectives?|Policy?|Primer?|Q&A?|Review?|Research Article?|Research in Translation?|Retraction?|Software?|Student Forum?|Synopsis?|Unsolved Myster.?|The PLoS Medicine Debate?)'

            typepat = re.compile(article_type_regex)
            try:
                articletype = re.search(typepat, prebody).group(1)
            except:
                try:
                    article_type_regex = re.escape(str(
                        fulldoi)) + '(Anniversary update?|Best Practice?|Book Reviews?|Case Report?|Collection?|Commentary?|Comment?|Community Page?|Correction?|Correspondence?|Editorial?|Education?|Essay?|Feature?|Focus?|Formal Comment?|Forum?|Guidelines and Guidance?|Health in Action?|Historical and Philosophical Perspectives?|Interview?|Journal Club?|Learning Forum?|Message from PLoS?|Message from the Founders?|Message from the PLoS Founders?|Meta-Research?|Methodology?|Neglected Diseases?|Obituary?|Online Only?|Online Quiz?|Opinion?|Perspectives?|Policy?|Primer?|Q&A?|Review?|Research Article?|Research in Translation?|Retraction?|Software?|Student Forum?|Synopsis?|Unsolved Myster.?|The PLoS Medicine Debate?)'
                    typepat = re.compile(article_type_regex)
                    articletype = re.search(typepat, prebody).group(1)
                except:
                    articletype = np.nan

            overall_list.append((abstract, body, bodystop, year, doi, pmid, txtfile, prebody, articletype))

        print("Making data frame")
        df_overall = pd.DataFrame(overall_list,
                                  columns=['abstract', 'body', 'bodystop', 'year', 'doi', 'pmid', 'txtfile', 'prebody',
                                           'articletype'])
        df_overall['journal'] = journalList[j]

        df_overall.to_json(outPath + journalList[j] + '.json')

        articletypes = pd.Series(df_overall.groupby('articletype').count().journal)
        articletypes.sort_values(inplace=True, ascending=False)
        articletypes.to_csv(outPath + journalList[j] + '_FreqArticleType.csv')


def parse_plosone(basePath, outPathONE):
    """
    Parsing fulltext articles from PloS ONE.

    Reads in fulltext .txts and extracts fulltext body and abstract as well as doi

    One caution about the way the chunking is being done: If there is an entry that is a correction at exactly the
    len(filelist) / chunkNumber multiple, then that gets skipped and the next chunk will be twice the normal size

    Output: JSON pandas dataframe in output directory plus csv containing article types extracted

    """

    if not os.path.exists(outPathONE):
        os.makedirs(outPathONE)

    journalList = ['PLoS_ONE']

    # Checkline regex
    tabpat = re.compile('\t')

    abstrpat = re.compile(
        '(?:provided the original work is properly cited|provided this notice is preserved along with the article\'s original URL|provided the original author and source are credited|modified, built upon, or otherwise used by anyone for any lawful purpose)')

    bodypat = re.compile('^(.*?)(==== Body\n|Editor\'s summary\n)')

    endpat = re.compile(
        '^([Ss]upplementary [Ii]nformation|[Ss]upplementary [Mm]aterial|[Ss]upporting [Ii]nformation|Abbreviations|Availability of supporting data|Authors\' contributions|Author contributions|Acknowledgements|Patient Summary|==== Refs)\n')

    temp_loc = 0  # Initialize location that is later updated to save chunks
    num_chunks = 64  # How many chunks should the final list be divided into?

    for j in range(0, len(journalList)):
        print("Parsing text files from journal " + journalList[j])
        # Get list of files
        fileList = []
        for file in os.listdir(basePath + journalList[j]):
            if file.endswith(".txt"):
                fileList.append(file)

        # overall_list = []
        part_list = []

        for i in range(0, len(fileList)):

            with io.open(basePath + journalList[j] + '/' + fileList[i], 'r', encoding='utf8') as file:
                output = []
                abstrpats = []
                bodypats = []
                endpats = []
                k = 0
                for line in file:  # read line by line
                    # output.append(line) # Uncomment this and comment next 4 lines if tables should stay in the texts
                    if re.search(tabpat, line) is None:
                        output.append(line)
                    else:
                        output.append('\n')
                    if re.search(abstrpat, line) is not None:
                        abstrpats.append(k)
                    if re.search(bodypat, line) is not None:
                        bodypats.append(k)
                    if re.search(endpat, line) is not None:
                        endpats.append(k)
                    k += 1

                if len(bodypats) > 1:
                    print(str(fileList[i]))

            try:
                abstract = unidecode.unidecode(' '.join(output[max(abstrpats) + 1: min(bodypats)]).replace('\n', ' '))
            except:
                abstract = np.nan

            try:
                if (len(endpats)) > 0:
                    body = unidecode.unidecode(' '.join(output[max(bodypats) + 1: min(endpats)]).replace('\n', ' '))
                else:
                    body = unidecode.unidecode(' '.join(output[max(bodypats) + 1:]).replace('\n', ' '))
            except:
                body = np.nan

            try:
                bodystop = unidecode.unidecode(' '.join(output[min(endpats):]).replace('\n', ' '))
            except:
                bodystop = np.nan

            try:
                prebody = unidecode.unidecode(' '.join(output[0: min(abstrpats + bodypats) + 1]).replace('\n', ' '))
            except:
                prebody = np.nan

            txtfile = fileList[i]  # save name of textfile for easier QC later on

            # Extract year from filename
            year = re.search("_([0-9]{4})_", txtfile).group(1)

            # doi pattern from http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
            try:
                doi = re.search("(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+)", prebody).group(1)
                doi = re.sub("[^\d]+$", '', doi)  # remove anything from the end of the doi if it ends with a string

                fulldoi = doi
                doi = re.sub("PMEDICINE.*", '',
                             doi)  # Also remove anything starting with PMEDICINE, which obfuscates later dois in PloS Med
                doi = re.sub("PBIOLOGY.*", '',
                             doi)  # Also remove anything starting with PMEDICINE, which obfuscates later dois in PloS Biol
                doi = re.sub("PONE-.*", '', doi)  #

                doi = re.sub("[0-9]{2}-PLME.*", '', doi)
                doi = re.sub("[0-9]{2}-PLBI.*", '', doi)

                doi = re.sub("plme.*", '', doi)
                doi = re.sub("plbi.*", '', doi)

            except:
                doi = np.nan

            try:
                pmid_regex = re.escape(re.search("\/(.*)", doi).group(
                    1)) + "(\d+)10\."  # This uses the previously extracted doi to look for the pmid
            except:
                pmid_regex = np.nan

            try:
                pmid = int(re.search(pmid_regex, prebody).group(1))
            except:
                pmid = np.nan

            article_type_regex = re.escape(str(
                doi)) + '(Anniversary update?|Best Practice?|Book Reviews?|Case Report?|Collection?|Commentary?|Comment?|Community Page?|Correction?|Correspondence?|Editorial?|Education?|Essay?|Feature?|Focus?|Formal Comment?|Forum?|Guidelines and Guidance?|Health in Action?|Historical and Philosophical Perspectives?|Interview?|Journal Club?|Learning Forum?|Message from PLoS?|Message from the Founders?|Message from the PLoS Founders?|Meta-Research?|Methodology?|Neglected Diseases?|Obituary?|Online Only?|Online Quiz?|Opinion?|Perspectives?|Policy?|Primer?|Q&A?|Review?|Research Article?|Research in Translation?|Retraction?|Software?|Student Forum?|Synopsis?|Unsolved Myster.?|The PLoS Medicine Debate?)'

            typepat = re.compile(article_type_regex)
            try:
                articletype = re.search(typepat, prebody).group(1)
                if articletype == 'Correction':
                    continue
            except:
                try:
                    article_type_regex = re.escape(str(
                        fulldoi)) + '(Anniversary update?|Best Practice?|Book Reviews?|Case Report?|Collection?|Commentary?|Comment?|Community Page?|Correction?|Correspondence?|Editorial?|Education?|Essay?|Feature?|Focus?|Formal Comment?|Forum?|Guidelines and Guidance?|Health in Action?|Historical and Philosophical Perspectives?|Interview?|Journal Club?|Learning Forum?|Message from PLoS?|Message from the Founders?|Message from the PLoS Founders?|Meta-Research?|Methodology?|Neglected Diseases?|Obituary?|Online Only?|Online Quiz?|Opinion?|Perspectives?|Policy?|Primer?|Q&A?|Review?|Research Article?|Research in Translation?|Retraction?|Software?|Student Forum?|Synopsis?|Unsolved Myster.?|The PLoS Medicine Debate?)'
                    typepat = re.compile(article_type_regex)
                    articletype = re.search(typepat, prebody).group(1)
                    if articletype == 'Correction':
                        continue
                except:
                    articletype = np.nan

            part_list.append((abstract, body, bodystop, year, doi, pmid, txtfile, prebody, articletype))

            # If the current i is divisible by len(fileList)/num_chunks without remainder or if it is the last element
            # in the file list, then make a dataframe with the current part_list
            if (i > 0 and i % math.ceil(len(fileList) / num_chunks) == 0) or (i == len(fileList) - 1):
                print("Making data frame")
                print("Length of current chunk is " + str(len(part_list)))
                df_part = pd.DataFrame(part_list,
                                       columns=['abstract', 'body', 'bodystop', 'year', 'doi', 'pmid', 'txtfile',
                                                'prebody', 'articletype'])
                df_part['journal'] = journalList[j]

                df_part.to_json(outPathONE + journalList[j] + '_' + str(i) + '.json')

                articletypes = pd.Series(df_part.groupby('articletype').count().journal)
                articletypes.sort_values(inplace=True, ascending=False)
                articletypes.to_csv(outPathONE + journalList[j] + '_' + str(i) + '_FreqArticleType.csv')

                print("Old temp loc is " + str(temp_loc))
                temp_loc = i
                print("New temp loc is " + str(temp_loc))

                # Clear part_list
                part_list = []




