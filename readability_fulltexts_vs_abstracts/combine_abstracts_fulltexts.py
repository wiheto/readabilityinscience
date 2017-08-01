"""
Function which compares abstracts and full texts
separately for Plos ONE and the other journals

Output: JSONs and CSVs for Plos ONE and the other journals separately as well as concatenated
"""


def combine_abstracts_fulltexts_one(abstractsPath, outPathONE, statsDir, abstractJournalONE, ftJournalsONE):
    """
    Compares readability metrics of abstracts and fulltexts.

    :param abstractsPath: Abstracts location
    :param outPathONE: Output path for PLoS ONE fulltext analysis
    :param statsDir: Output path for final dataframes
    :param abstractJournalONE: Name of PLoS ONE for abstracts ('plos_one[journal]')
    :param ftJournalsONE: Name of partial PLoS ONE files for fulltexts

    :return: Dataframes (json/csv) with combined abstracts + fulltexts data for PLoS ONE

    """

    import pandas as pd

    print("Comparing abstracts and fulltexts for PLoS ONE")

    ending = '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/'

    df_abstracts = pd.read_json(abstractsPath + abstractJournalONE + ending + 'lang.json')
    df_searchresults = pd.read_json(abstractsPath + abstractJournalONE + ending + 'searchresults')

    df_abstracts_pmid = pd.merge(df_abstracts, df_searchresults, on='pmid', how='inner')
    df_abstracts_pmid['pmid'] = df_abstracts_pmid['pmid'].astype('unicode')

    # Take average of wordLength and sylCount
    df_abstracts_pmid['sumSylCount'] = df_abstracts_pmid['sylCount'].apply(
        lambda row: sum(row) if row is not None else None)

    # Rename columns
    df_abstracts_pmid = df_abstracts_pmid.rename(columns={'flesch': 'flesch_abs', 'NDC': 'NDC_abs', 'year': 'year_abs',
                                                          'wordLength': 'wordLength_abs',
                                                          'wordCount': 'wordCount_abs',
                                                          'sentenceCount': 'sentenceCount_abs',
                                                          'sylCount': 'sylCount_abs',
                                                          'sumSylCount': 'sumSylCount_abs',
                                                          'PercDiffWord': 'PercDiffWord_abs'})

    for j in range(0, len(ftJournalsONE)):
        df_ft_temp = pd.read_json(outPathONE + 'metrics/' + 'PLoS_ONE/' + ftJournalsONE[j] + '_metrics.json')
        if j == 0:
            df_fulltexts_pmid = df_ft_temp
        else:
            df_fulltexts_pmid = pd.concat([df_fulltexts_pmid, df_ft_temp])

    # Take average of wordLength and sylCount
    df_fulltexts_pmid['sumSylCount'] = df_fulltexts_pmid['sylCount'].apply(
        lambda row: sum(row) if row is not None else None)

    # Rename columns
    df_fulltexts_pmid = df_fulltexts_pmid.rename(columns={'flesch': 'flesch_ft', 'NDC': 'NDC_ft', 'year': 'year_ft',
                                                          'wordLength': 'wordLength_ft',
                                                          'wordCount': 'wordCount_ft',
                                                          'sentenceCount': 'sentenceCount_ft',
                                                          'sylCount': 'sylCount_ft',
                                                          'sumSylCount': 'sumSylCount_ft',
                                                          'PercDiffWord': 'PercDiffWord_ft'})

    df_fulltexts_pmid.pmid = df_fulltexts_pmid.pmid.fillna(0.0).astype(float).astype(int)
    df_abstracts_pmid.pmid = df_abstracts_pmid.pmid.fillna(0.0).astype(float).astype(int)

    # Merge into one dataframe by id (either pmid or doi or both)
    df_final = pd.merge(df_abstracts_pmid, df_fulltexts_pmid, on='pmid', how='inner')

    # Add journal name
    df_final['journal'] = 'PLoS_ONE'

    # http://stackoverflow.com/questions/28901683/pandas-get-rows-which-are-not-in-other-dataframe
    df1 = df_fulltexts_pmid
    df2 = df_abstracts_pmid
    missing = df1[(~df1.pmid.isin(df2.pmid))]
    missing_nonNA = missing[~missing.pmid.isnull()]
    print(missing_nonNA.pmid)

    print(str(round((1 - len(df_final) / min(len(df_fulltexts_pmid), len(df_abstracts_pmid))) * 100,
                    2)) + '%' + ' of cases lost in matching')

    df_final = df_final[~df_final['flesch_abs'].isnull() & ~df_final['flesch_ft'].isnull()]

    # Subset to years 2015 and older
    df_final = df_final.loc[(df_final.year_abs <= 2015)]

    # Reduce dataframe to some key metrics
    df_plos = df_final[['NDC_abs', 'NDC_ft', 'flesch_abs', 'flesch_ft', 'year_abs', 'pmid', 'wordCount_abs',
                        'wordCount_ft', 'sentenceCount_abs', 'sentenceCount_ft', 'sumSylCount_abs', 'sumSylCount_ft',
                        'PercDiffWord_abs', 'PercDiffWord_ft', 'journal']]

    df_plos.to_json(statsDir + 'PLoS_ONE.json')


def combine_abstracts_fulltexts_others(abstractsPath, outPath, statsDir, abstractJournalsOthers, ftJournals):
    """
    Compare abstracts and fulltexts for the rest of the fulltext journals.

    :param abstractsPath: Abstracts location
    :param outPath: Output path for fulltext analysis
    :param statsDir: Output path for final dataframes
    :param abstractJournalOthers: List of journals for abstracts
    :param ftJournals: List of journals for fulltexts

    :return: Dataframes (json/csv) with combined abstracts + fulltexts data from the rest of the fulltext journals

    """

    import pandas as pd

    print("Comparing abstracts and fulltexts for the other OA journals")

    ending = '/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/'

    for i in range(0,len(abstractJournalsOthers)):

        # Load in abstracts
        df_abstracts = pd.read_json(abstractsPath + abstractJournalsOthers[i] + ending + 'lang.json')
        df_searchresults = pd.read_json(abstractsPath + abstractJournalsOthers[i] + ending + 'searchresults')

        df_abstracts_pmid = pd.merge(df_abstracts, df_searchresults, on='pmid', how='inner')
        df_abstracts_pmid['pmid'] = df_abstracts_pmid['pmid'].astype('unicode')

        # Take average of wordLength and sylCount
        df_abstracts_pmid['sumSylCount'] = df_abstracts_pmid['sylCount'].apply(lambda row: sum(row) if row is not None else None)

        # Rename columns
        df_abstracts_pmid = df_abstracts_pmid.rename(columns={'flesch': 'flesch_abs', 'NDC': 'NDC_abs', 'year': 'year_abs',
                                                              'wordLength': 'wordLength_abs',
                                                              'wordCount': 'wordCount_abs',
                                                              'sentenceCount': 'sentenceCount_abs',
                                                              'sylCount': 'sylCount_abs',
                                                              'sumSylCount': 'sumSylCount_abs',
                                                              'PercDiffWord': 'PercDiffWord_abs'})

        # Load in full texts
        df_fulltexts_pmid = pd.read_json(outPath + 'metrics/' + ftJournals[i] + '_metrics.json')

        # Take average of wordLength and sylCount
        df_fulltexts_pmid['sumSylCount'] = df_fulltexts_pmid['sylCount'].apply(lambda row: sum(row) if row is not None else None)

        # Rename columns
        df_fulltexts_pmid = df_fulltexts_pmid.rename(columns={'flesch': 'flesch_ft', 'NDC': 'NDC_ft', 'year': 'year_ft',
                                                              'wordLength': 'wordLength_ft',
                                                              'wordCount': 'wordCount_ft',
                                                              'sentenceCount': 'sentenceCount_ft',
                                                              'sylCount': 'sylCount_ft',
                                                              'sumSylCount': 'sumSylCount_ft',
                                                              'PercDiffWord': 'PercDiffWord_ft'})

        df_fulltexts_pmid.pmid = df_fulltexts_pmid.pmid.fillna(0.0).astype(float).astype(int)
        df_abstracts_pmid.pmid = df_abstracts_pmid.pmid.fillna(0.0).astype(float).astype(int)

        # Merge into one dataframe by id (either pmid or doi or both)
        df_final = pd.merge(df_abstracts_pmid, df_fulltexts_pmid, on='pmid', how='inner')

        # http://stackoverflow.com/questions/28901683/pandas-get-rows-which-are-not-in-other-dataframe
        df1 = df_fulltexts_pmid
        df2 = df_abstracts_pmid
        missing = df1[(~df1.pmid.isin(df2.pmid))]
        missing_nonNA = missing[~missing.pmid.isnull()]
        print(missing_nonNA.pmid)

        print(str(round((1 - len(df_final) / min(len(df_fulltexts_pmid), len(df_abstracts_pmid))) * 100, 2)) + '%' + ' of cases lost in matching')

        df_final = df_final[~df_final['flesch_abs'].isnull() & ~df_final['flesch_ft'].isnull()]

        # Subset to years 2015 and older
        df_final = df_final.loc[(df_final.year_abs <= 2015)]

        # Add journal name
        df_final['journal'] = ftJournals[i]

        # Reduce dataframe to some key metrics
        df_final = df_final[['NDC_abs', 'NDC_ft', 'flesch_abs', 'flesch_ft', 'year_abs', 'pmid', 'wordCount_abs',
                             'wordCount_ft', 'sentenceCount_abs', 'sentenceCount_ft', 'sumSylCount_abs',
                             'sumSylCount_ft', 'PercDiffWord_abs', 'PercDiffWord_ft', 'journal']]

        # add other journals together
        if i == 0:
            df_others = df_final
        else:
            df_others = pd.concat([df_others, df_final], ignore_index=True)

    df_others.to_json(statsDir + 'others.json')


def combine_others_one(statsDir):
    """
    Combine all output files into one big json/csv.

    """

    import pandas as pd

    print("Combining everything into one final output dataframe")

    df_others = pd.read_json(statsDir + 'others.json')
    df_plos = pd.read_json(statsDir + 'PLoS_ONE.json')

    df_all = pd.concat([df_plos, df_others], ignore_index=True)

    df_all.to_json(statsDir + 'all_fulltextabstract_NDC_Flesch_year.json')
    df_all.to_csv(statsDir + 'all_fulltextabstract_NDC_Flesch_year.csv', index=False)