def convert_id(df, id_in, id_out, chunklength, timer, load_loc, save_loc=None, load_pmid=True,
               mail_ad='placeholder', tool='id_converter'):
    """
    Function to convert between doi, pmid (and PMC) either using prespecified mappings or using the PubMed API

    For reproducibility reasons, the script loads by default (load_pmid parameter) a saved doi -> pmid mapping
    from a csv specified in load_loc, i.e. does not go through PubMed to do the conversions. If that is desired,
    load_pmid needs to be changed to False (and load_loc=None) instead.

    Feed in dataframe df that contains a column 'doi' or 'pmid', specify from what (id_in) to what (id_out)
    should be converted, add your mail address (mail_ad) and a toolname (tool) and specify a chunklength, i.e.
    how many IDs are converted at once, Pubmed max is 200 (but I had problems with Plos Biol with that,
    so 100 should be default) and the timer to wait between requests in seconds (timer).
    Optional argument save_loc can be set if the obtained mappings should be saved

    When specifying xx = convert_id(...) then the output in xx is the originally fed in dataframe with an added column
    of id_out (if that was already in the original dataframe it will be added as e.g. "pmid_y")

    Example call:
    convert_id(df_data, 'doi', 'pmid', 100, 2, load_loc=idPath + 'all_ids.csv')
    """

    import time
    import requests
    import pandas as pd
    import numpy as np

    pubmedURL = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=' + tool + '&email=' + mail_ad + '&ids='

    # Format changes
    try:
        df[id_in] = df[id_in].fillna(value=np.nan)  # If there are any None objects
    except:
        pass

    try:
        df[id_out] = df[id_out].fillna(value=np.nan)
        df[id_out] = df[id_out].fillna(0.0).astype(int).astype(str)
    except:
        pass

    # If there is a location for a csv dataframe with doi -> pmid mappings
    if load_pmid:
        df_mappings = pd.read_csv(load_loc)
        df_final = pd.merge(df, df_mappings, on=id_in, how='inner')  # or "left"?
        print("Number of final dataframe entries: " + str(len(df_final)))

    else:
        print("Could not find .csv with doi -> pmid mappings, retrieving mappings from Pubmed")
        # need to remove NaNs because the pubmed API does not accept these requests
        df_nonna = df[~df[str(id_in)].isnull()].reset_index()
        dois_to_convert = df_nonna[str(id_in)].values
        # Split into evenly sized chunks
        doi_chunked = [dois_to_convert[i:i+chunklength] for i in range(0, len(dois_to_convert), chunklength)]

        original_list = []
        response_list = []

        for i in range(0, len(doi_chunked)):
            cur_request = pubmedURL + str(",".join(doi_chunked[i])) + '&format=json'
            response = requests.get(cur_request)
            json_data = response.json()

            for j in range(0, len(doi_chunked[i])):
                try:
                    original_list.append(json_data['records'][j][str(id_in)])
                except:
                    original_list.append(np.nan)
                    print("Problem in input ID")
                try:
                    response_list.append(json_data['records'][j][str(id_out)])
                except:
                    response_list.append(np.nan)
                    try:
                        print("Problem in conversion - input ID was " + str(json_data['records'][j][str(id_in)]))
                    except:
                        print("Problem in conversion - no input ID?")

            print('Waiting ' + str(timer) + ' seconds, about ' + str((len(doi_chunked)-i) * timer) + ' seconds left.')
            time.sleep(timer)

        # Make dataframe
        df_responselist = pd.DataFrame({str(id_in) : original_list, str(id_out) : response_list})

        # Save this dataframe for reproducibility
        if save_loc:
            df_responselist.to_csv(save_loc, index=False)

        # Recombine with original input df
        df_final = pd.merge(df, df_responselist, on=str(id_in), how='outer')

    return df_final
