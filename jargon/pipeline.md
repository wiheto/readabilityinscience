The order these scripts should be run in order - otherwise there will be files missing that get saved in the previous step.

__NB:__ For these scripts to work, the download_data scripts need to be run to have the abstracts.

1. scienceEasyWords_derive.py - find the most commonly used words on a sample of 12,000. If no new dataset is going to be created, this script can be omitted. __NB:__ that an additional csv is created through manual voting of words after this step. to create the jargon list. This is called "jargonListFinal.csv". The one used in the analysis is supplied with the the files. If a new list is generated, then a new document has to be created.
2. scienceEasyWords_test.py - quantify the % of each word.
3. plot_verification_vs_training.py - plot how similar two different 12,000 datasets are
4. plot_scienceEasyWords.py - plot the figures used in article
5. scienceEasyWords_test_examples.py - plot the example words.
