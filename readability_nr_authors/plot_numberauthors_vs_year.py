
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.colors import LogNorm

authorDat=pd.read_csv('./data/abstracts/nrAuthors_Flesch_NDC.csv')



year = np.arange(1880,2017)

authorMat = np.zeros([len(year),10])
fleschMat = np.zeros([len(year),10])-1000
ndcMat = np.zeros([len(year),10])-1000

for r in range(0,len(authorDat)):
    authorMat[year==authorDat['year'][r],int(authorDat['nrAuthors'][r])-1]=authorDat['n'][r]
    if authorDat['n'][r]>10:
        fleschMat[year==authorDat['year'][r],int(authorDat['nrAuthors'][r])-1]=authorDat['Flesch'][r]
        ndcMat[year==authorDat['year'][r],int(authorDat['nrAuthors'][r])-1]=authorDat['NDC'][r]

for n in range(0,authorMat.shape[0]):
    authorMat[n,:]=authorMat[n,:]/np.sum(authorMat[n,:])


NUM_COLORS = 10

authorMat[np.isnan(authorMat)]=0


cm = plt.get_cmap('nipy_spectral')

fig,ax=plt.subplots(1)
#ax.set_ylim(0,1)
ax.set_xlim(1880,2016)
ax.set_color_cycle([cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)])
stack=ax.stackplot(year,np.transpose(authorMat))
ax.set_ylabel('Percent of articles')
ax.set_xlabel('Years')
ax.set_ylim([0,1])
ax.set_xlim([1880,2016])

fig.legend(handles=stack,labels=np.arange(1,11))
fig.savefig('./figures/fig5a.png')
fig.savefig('./figures/fig5a.eps')

fig,ax = plt.subplots(1,1,figsize=(16, 3),dpi=600)

my_cmap = plt.cm.get_cmap('inferno_r')
#my_cmap.set_bad([0.9176,0.9176,0.95])

my_cmap.set_under([.9176,0.9176,0.95])


#sns.heatmap(yearcount+1e-1,ax=ax[0],norm = LogNorm(vmin=yearcount.min(), vmax=yearcount.max()),cmap='inferno')
pc1=ax.pcolormesh(year,np.arange(0,11),np.transpose(fleschMat),cmap=my_cmap,linewidth=0,vmin=5,vmax=35)
pc1.set_rasterized(True)

ax.set_xticks(np.arange(1880,2020,20))
ax.set_xticklabels(np.arange(1880,2020,20))
ax.set_yticklabels('')
ax.set_xlim([1880,2016])
ax.set_ylabel('Number of articles',rotation=90)
ax.set_ylabel('Year')
fig.colorbar(pc1,ax=ax)

fig.savefig('./figures/fig5c.png')
fig.savefig('./figures/fig5c.pdf')



fig,ax = plt.subplots(1,1,figsize=(16, 3),dpi=600)

my_cmap = plt.cm.get_cmap('inferno')
#my_cmap.set_bad([0.9176,0.9176,0.95])

my_cmap.set_under([.9176,0.9176,0.95])


#sns.heatmap(yearcount+1e-1,ax=ax[0],norm = LogNorm(vmin=yearcount.min(), vmax=yearcount.max()),cmap='inferno')
pc1=ax.pcolormesh(year,np.arange(0,11),np.transpose(ndcMat),cmap=my_cmap,linewidth=0,vmin=11,vmax=13.5)
pc1.set_rasterized(True)

ax.set_xticks(np.arange(1880,2020,20))
ax.set_xticklabels(np.arange(1880,2020,20))
ax.set_yticks([1,10])
ax.set_xlim([1880,2020])
ax.set_xlabel('Year')
ax.set_ylabel('Number of authors',rotation=90)
fig.colorbar(pc1,ax=ax)

fig.savefig('./figures/fig5c-suppl1.pdf')
