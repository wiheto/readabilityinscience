# readabilityinscience

Article published in elife: https://elifesciences.org/articles/27725

Code is written in Python and R.

For python (3.x) is needed. Some changes will be needed for python (2.x).

### FAQ

_Why is the abstract data from PubMed not available?_

We have not shared the raw abstract texts because we do not want to breach any copyright. We have shared the rest of the data used in the analysis (e.g. all the language metrics such as "number of sentences" for each article). This data also includes pubmed ids for the article.

_When is the PubMed data needed?__

It depends what you want to do. If you wan to recalculate the different language metrics, derive a new science common words list, or perform a new analysis on the text. Anything else can be done with the data we provide in this repo.  

_Why does it only download 200 articles at a time?_

When the code was written, 10,000 articles could be downloaded at a time. Something changed in the efetch/pubmed tools around September 2016 and it fails to return any articles if it is larger than 200 or 250 articles. So we changed this to 200 as the default. This means the data takes a while to download.

_The scraper downloads more files than you use in your article_

The scraper downloads all the articles it can. And we only used articles from 2015 and earlier. If you run it now, you will get articles from 2017. So you will always download more articles. To get the exact same dataset as we used, select all the PMIDs that we use.

_Scrapers can stop working if the website the scrape changes, will this be supported?_

Scrapers can change with time. If PubMed makes some change we cannot promise we have the time to update this script. If the change is minor, it can be updated. But we are unable to promise to maintain a scraper for PubMed indefinitely. The PMIDs to download our data will always be available via github. Also the data files of the readability of different articles are available.

_A script is trying to load data that cannot be found?_

Most the scripts are intended to be run in the repository's main directory (i.e. /somewhere/on/your/computer/readabilityinscience/). Some scripts ask you to specify this directory first (specifically the download scripts. This is to be certain everything gets downloaded in the right place). So first, make sure you are running in the correct directory.

If this doesn't work. Leave an issue. When moving this data to the public repo and merging are respective workspaces, some paths were changed to assist anyone using the code. There may be some case when a path failed to be updated. If an issue here is found, we will update the code.


_Some PMIDs are missing in the dataset I have downloaded compared to your dataset_

When publishing this repo, we realized that this *could* theoretically happen (not confirmed/found but purely speculative at present). PMIDs can be updated at times (e.g. correction of an article). The scraper takes only one of the PMID per article. So it is theoretically possible that PubMed updates its records meaning the lists are no longer compatible. Unless pubmed indexes/indexed new articles from 2015 after we downloaded the original dataset, then the lists should be the same. What is the solution *if* this occurs? The PMIDs we used are available in the data folder and they can be used with the scraper to download the exact same files instead of journal name. If this happens, please let us know.

_I get slightly different values than in your article (and I use Windows)_

Treetagger has different definitions for linux and windows. Our analysis used linux. Using windows will lead to slight differences in parsing of sentences.

_I came from the link in the biorxiv article looking for supplementary data_

For now the supplementary tables not included in the bioRxiv manuscript are included in ./data. S01_JournalSelection is /data/biorxiv/JournalSelection.xlsx. S07_WordLists is /data/biorxiv/WordLists.xlsx. Note that these documents are out of date. They got changed during the review process and they are updated elsewhere iin this repo with the later version.
