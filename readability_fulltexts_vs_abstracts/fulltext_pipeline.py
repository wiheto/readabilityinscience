
"""

--- Main fulltext processing pipeline ---

Be aware: Running the whole pipeline can take 16++ hours, depending on number of processors assigned, setting 5+
processors is beneficial

General prerequisites:
    Python >= 3.5
    NLTK == 3.2.2
    Treetagger == 3.2 Linux
    Treetaggerwrapper == 2.2.2
    NLTK datasets (nltk.download()) and specified TreeTagger directory
    (following instructions at http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/)
    NB: Treetagger 3.2 on Windows is currently not supported due to version differences with the Linux version
    of Treetagger 3.2

Processing steps:
    1) Download PMC Open Access Subset: https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/
    2) Either download abstracts separately for the journals to be analyzed (using get_pubmeddata from
       dataminingfunctions) or extract them from the fulltexts directly
    3) Put fulltext textfiles into subfolders for each journal in ../data/fulltexts/*** (where *** are the ftJournals
       names below) and the abstracts file ("searchresults") into ../data/fulltexts/abstracts/*** with
       subfolders "/id_article/abstracttext_pubdate_year_pmid_articletitle_journal_title_keyword_doi/searchresults"
       (where *** are the abstractsJournals names specified below)
    4) Make sure that provided doi -> pmid matching .csvs are in basePath/ids/ (default ../data/fulltexts/ids/) to
       reproduce our analysis, otherwise ID matching can also be done by calling the Pubmed API, check convert_id.py
    5) Set numProc parameter to number of processors to be assigned to the task (default is 4,
       but 5+ is recommended if possible)

Output:
    .json and .csv dataframes in statsDir (default output path is "../data/fulltexts/stats/")

"""

from multiprocessing import Pool
from functools import partial
import os
import sys
sys.path.append('../')

from readability_fulltexts_vs_abstracts import parse_fulltexts as pf
from readability_fulltexts_vs_abstracts import analyze_fulltexts as af
from readability_fulltexts_vs_abstracts import combine_abstracts_fulltexts as caf

# Initialize variables

# Number of processors for multithreading
numProc = 4

basePath = '../data/fulltexts/'
outPath = basePath + 'output/'
outPathONE = outPath + 'PLoS_ONE/'
abstractsPath = basePath + 'abstracts/'
statsDir = basePath + 'stats/'
idPath = basePath + 'ids/'

ftJournals = ['BMC_Biol', 'eLife', 'Genome_Biol', 'PLoS_Med', 'PLoS_Biol']
abstractJournalsOthers = ['bmc_biol[journal]', 'elife[journal]', 'genome_biol[journal]',
                          'plos_med[journal]', 'plos_biol[journal]']
abstractJournalONE = 'plos_one[journal]'

# For id conversion at Pubmed (not necessary with defaults if doi -> pmid csv mappings exist)
email = 'placeholder'
tool = 'id_converter'

if not os.path.exists(outPath + 'metrics/'):
    os.makedirs(outPath + 'metrics/')

if not os.path.exists(outPath + 'pmid/'):
    os.makedirs(outPath + 'pmid/')

if not os.path.exists(outPathONE + 'pmid/'):
    os.makedirs(outPathONE + 'pmid/')

if not os.path.exists(idPath):
    os.makedirs(idPath)

if not os.path.exists(outPathONE + 'metrics/' + 'PLoS_ONE/'):
    os.makedirs(outPathONE + 'metrics/' + 'PLoS_ONE/')

if not os.path.exists(statsDir):
    os.makedirs(statsDir)

if __name__ == '__main__':

    # Parse raw text files
    pf.parse_bmc(basePath, outPath)
    pf.parse_elife(basePath, outPath)
    pf.parse_genbiol(basePath, outPath)
    pf.parse_plos(basePath, outPath)
    pf.parse_plosone(basePath, outPathONE)

    # Make list of parsed jsons from PLoS ONE
    ftJournalsONE = [t[:-5] for t in os.listdir(outPathONE) if t.endswith('.json')]

    # Other journals convert_id
    af.convert_id_others(outPath, idPath, ftJournals)

    # Other journals abstracts analysis
    pool = Pool(processes=numProc)  # Create multiprocessing Pool
    partialAbstracts = partial(af.analyze_abstracts_others, abstractsPath)  # Partial needed for additional arguments
    pool.map(partialAbstracts, abstractJournalsOthers)  # Map jsons to workers
    pool.close()

    # Other journals fulltexts analysis
    pool = Pool(processes=numProc)  # Create multiprocessing Pool
    partialFulltexts = partial(af.analyze_ft_others, outPath)  # Partial needed for additional arguments
    pool.map(partialFulltexts, ftJournals)  # Map jsons to workers
    pool.close()

    # PLoS ONE convert_id
    af.convert_id_plosone(outPathONE, idPath, ftJournalsONE)

    # PLoS ONE abstracts analysis
    af.analyze_abstracts_plosone(abstractsPath, abstractJournalONE)

    # PLoS ONE fulltexts analysis
    pool = Pool(processes=numProc)  # Create multiprocessing Pool
    partialFTONE = partial(af.analyze_ft_plosone, outPathONE)  # Partial is needed for additional arguments
    pool.map(partialFTONE, ftJournalsONE)  # Map jsons to workers
    pool.close()

    # Combine abstracts and fulltexts into a single dataframe
    caf.combine_abstracts_fulltexts_one(abstractsPath, outPathONE, statsDir, abstractJournalONE, ftJournalsONE)
    caf.combine_abstracts_fulltexts_others(abstractsPath, outPath, statsDir, abstractJournalsOthers, ftJournals)
    caf.combine_others_one(statsDir)
