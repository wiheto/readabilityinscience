import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load words
ew=pd.read_csv('./jargon/scienceEasyWords.csv')


# Print the percentrange which training dataset overlaps with verifcation
scienceList_inboth = set(ew.Training).intersection(list(ew.Verification))
JustificationOverlapInPercent=100*len(scienceList_inboth)/len(ew)
print(JustificationOverlapInPercent)


# The stability of the analysis through time was also checkedd for sanity (although not included in the analysis).
# The idea was to validate that there is no sharp cut off when the lists no longer validate with each other or if there was an obvious peak that could restrain the analysis
# No obvious peak was found so it was decided that using the same number of Science Common Words as the NDC easy words made the most sense.
# There is probabaly a much quicker way to do this. I feel quite stupid
overlapVerification = np.zeros(len(ew))
for n in range(1,1+len(ew)):
    scienceList_inboth = set(ew.Training[:n]).intersection(list(ew.Verification[:n]))
    overlapVerification[n-1]=len(scienceList_inboth)/n

#Plot overlap of training and verification set (This figure was not used in analysis)
fig,ax=plt.subplots(1)
ax.plot(overlapVerification*100)
ax.set_ylabel('percent overlap between verifcation and training data')
ax.set_xlabel('words in list')
fig.savefig('./jargon/verificationdatasetoverlap.png')
