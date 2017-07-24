def convert_id_others(outPath, idPath, ftJournals):
    """
    Convert IDs from doi to pmid.

    :param outPath: Original journal json directory
    :param idPath: Location of .csv file with mappings of doi -> pmid
    :param ftJournals: Journals to be processed
    :return: Writes out dataframe at outPathPmid which includes a pmid column

    """

    from functions import convert_id
    import pandas as pd

    for i in range(0, len(ftJournals)):

        print("Converting IDs of journal " + ftJournals[i])

        inPath = outPath + ftJournals[i] + '.json'
        outPathPmid = outPath + 'pmid/' + ftJournals[i] + '.json'

        df_fulltexts = pd.read_json(inPath)

        try:
            df_fulltexts.drop('pmid', axis=1, inplace=True)
        except:
            pass

        # Convert fulltext dois to pmids, the try/except is for Pubmed downloads which sometimes don't work
        try:
            df_fulltexts_pmid = convert_id.convert_id(df_fulltexts, 'doi', 'pmid', 100, 2,
                                                      load_loc=idPath + 'all_ids.csv')
        except:
            df_fulltexts_pmid = convert_id.convert_id(df_fulltexts, 'doi', 'pmid', 100, 2,
                                                      load_loc=idPath + 'all_ids.csv')

        df_fulltexts_pmid.to_json(outPathPmid)


def analyze_abstracts_others(abstractsPath, name):
    """
    Calculate readability metrics for abstracts.

    :param abstractsPath: Raw abstracts directory
    :param name: Name of journal
    :return: Dataframe with calculated readability metrics: lang.json at outPathAbstracts

    """

    from functions import readabilityFunctions as rf
    import treetaggerwrapper

    print("Processing abstracts of journal " + name)

    inPathAbstracts = abstractsPath + name + \
                      '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/searchresults'
    outPathAbstracts = abstractsPath + name + \
                       '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/lang.json'

    rf.analyze(path=inPathAbstracts, spath=outPathAbstracts,
               tagger=treetaggerwrapper.TreeTagger(TAGLANG='en'), textType='abstracttext')


def analyze_ft_others(outPath, name):
    """
    Calculate readability metrics for fulltexts.

    :param outPath: Raw fulltext directory
    :param name: Name of journal to be processed
    :return: Dataframe with calculated readability metrics for fulltexts in outPath/metrics/

    """

    from functions import readabilityFunctions as rf
    import treetaggerwrapper

    print("Processing fulltexts of journal " + name)

    inPath = outPath + 'pmid/' + name + '.json'
    outPathMetrics = outPath + 'metrics/' + name + '_metrics.json'

    rf.analyze(path=inPath, spath=outPathMetrics, tagger=treetaggerwrapper.TreeTagger(TAGLANG='en'), textType='body',
               columnList={'year', 'pmid', 'doi', 'strippedText', 'wordLength', 'wordCount', 'sentenceCount',
                           'sylCount', 'flesch', 'NDC', 'PercDiffWord', 'DiffWord_lst'})


def convert_id_plosone(outPathONE, idPath, ftJournalsONE):
    """
    Converting IDs from doi to pmid.

    :param outPathONE: Original PLoS ONE json directory
    :param idPath: Location of .csv file (doi_pmid_list_plosONE.csv) with mappings of doi -> pmid
    :param ftJournalsONE: Partial PLoS ONE journal jsons to be processed
    :return: Writes out dataframe at outPathPmidONE which includes a pmid column

    """

    from functions import convert_id
    import pandas as pd
    import os

    df_doi_pmid = pd.DataFrame(columns=['doi', 'pmid'])
    for i in range(0, len(ftJournalsONE)):

        print("Converting IDs of partial PLoS ONE file " + ftJournalsONE[i])

        inPath = outPathONE + ftJournalsONE[i] + '.json'
        outPathPmidONE = outPathONE + 'pmid/' + ftJournalsONE[i] + '.json'

        df_fulltexts = pd.read_json(inPath)

        try:
            df_fulltexts.drop('pmid', axis=1, inplace=True)
        except:
            pass

        # Convert fulltext dois to pmids
        try:
            df_fulltexts_pmid = convert_id.convert_id(df_fulltexts, 'doi', 'pmid', 100, 2,
                                                      load_loc=idPath + 'all_ids.csv')
        except:
            df_fulltexts_pmid = convert_id.convert_id(df_fulltexts, 'doi', 'pmid', 100, 2,
                                                      load_loc=idPath + 'all_ids.csv')

        df_fulltexts_pmid.to_json(outPathPmidONE)

        df_doi_pmid = df_doi_pmid.append(df_fulltexts_pmid[['doi', 'pmid']])

    if not os.path.exists(outPathONE + 'pmid/' + 'tmp/'):
        os.makedirs(outPathONE + 'pmid/' + 'tmp/')
    df_doi_pmid.to_csv(outPathONE + 'pmid/' + 'tmp/' + 'doi_pmid_list_plosONE.csv', index=False)
    df_doi_pmid_sorted = df_doi_pmid.sort_values('pmid')
    df_doi_pmid_sorted.to_csv(outPathONE + 'pmid/' + 'tmp/' + 'doi_pmid_list_sorted_plosONE.csv', index=False)


def analyze_abstracts_plosone(abstractsPath, abstractJournalONE):
    """
    Calculate readability metrics for abstracts for PLoS ONE.

    :param abstractsPath: Raw abstracts directory
    :param abstractJournalONE: Name of PLoS ONE abstract directory
    :return: Dataframe with calculated readability metrics: lang.json at outPath

    """

    from functions import readabilityFunctions as rf
    import treetaggerwrapper

    print("Processing abstracts of " + abstractJournalONE)

    inPathAbstracts = abstractsPath + abstractJournalONE + \
                      '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/searchresults'
    outPathAbstracts = abstractsPath + abstractJournalONE + \
                       '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/lang.json'

    rf.analyze(path=inPathAbstracts, spath=outPathAbstracts, tagger=treetaggerwrapper.TreeTagger(TAGLANG='en'),
               textType='abstracttext')


def analyze_ft_plosone(outPathONE, name):
    """
    Calculate readability metrics for fulltexts for PLoS ONE.

    :param outPathONE: Raw fulltext directory
    :param name: Name of partial PLoS ONE json
    :return: Dataframe with calculated readability metrics for fulltexts in outPathONE/metrics/

    """

    from functions import readabilityFunctions as rf
    import treetaggerwrapper

    print("Processing fulltexts of partial PLoS ONE file " + name)
    inPath = outPathONE + 'pmid/' + name + '.json'
    outPathMetrics = outPathONE + 'metrics/' + 'PLoS_ONE/' + name + '_metrics.json'

    rf.analyze(path=inPath, spath=outPathMetrics, tagger=treetaggerwrapper.TreeTagger(TAGLANG='en'), textType='body',
               columnList={'year', 'pmid', 'doi', 'strippedText', 'wordLength', 'wordCount', 'sentenceCount',
                           'sylCount', 'flesch', 'NDC', 'PercDiffWord', 'DiffWord_lst'})