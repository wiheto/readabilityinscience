import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LogNorm
from matplotlib.colors import LinearSegmentedColormap
dat=pd.read_csv('./data/abstracts/concatenatedLangData.csv')

# Script that just plots the descriptions about the data (fig1bc)

dat.sort_index(inplace=True)
dat=dat.drop(dat.index[dat.year>=2016]) #Drop 2016 out of the analysis which is still there >< (usually done at plotting, but now needs to be done as otherwise

ydat = dat.groupby('year')

nrJournals = len(np.unique(dat.journalID))

startyear = np.zeros(nrJournals)
jlen = np.zeros(nrJournals)
for n in range(0,nrJournals):
    startyear[n]=dat[dat.journalID==n]['year'].min()
    jlen[n]=len(dat[dat.journalID==n]['year'])

yearrange=np.arange(1880,2017)
yearcount=np.zeros(len(yearrange))
ytmp=ydat.count()['index']
for i,n in enumerate(ytmp.index):
    yearcount[yearrange==n]=ytmp.values[i]

yearcountstart=np.zeros(len(yearrange))
for n in startyear:
    yearcountstart[np.where(yearrange==n)[0]]+=1
yearcountstart[yearcountstart==0]=-1

yearcount=np.vstack([yearcount,yearcount])
yearcountstart=np.vstack([yearcountstart,yearcountstart])

yearcount[yearcount==0]=-20


fig,ax = plt.subplots(2,1,figsize=(16, 3),dpi=600)

my_cmap = plt.cm.get_cmap('inferno')
my_cmap.set_under([1,1,1])
my_cmap.set_bad([1,1,1])

colors_restrained = my_cmap(np.linspace(0, 0.75, my_cmap.N // 2))
cmap2 = LinearSegmentedColormap.from_list('Upper Half', colors_restrained)
cmap2.set_under([1,1,1])
cmap2.set_bad([1,1,1])

#sns.heatmap(yearcount+1e-1,ax=ax[0],norm = LogNorm(vmin=yearcount.min(), vmax=yearcount.max()),cmap='inferno')
pc1=ax[0].pcolormesh(yearrange,np.arange(0,2),yearcount,cmap=my_cmap,norm=LogNorm(),linewidth=0)
pc1.set_rasterized(True)
ax[0].set_xticks(np.arange(1880,2016,20))
ax[0].set_xticklabels(np.arange(1880,2016,20))
ax[0].set_yticklabels('')
ax[0].set_ylim([0,1])
ax[0].set_xlim([1880,2016])
ax[0].set_ylabel('Number of articles',rotation=90)
fig.colorbar(pc1,ax=ax[0])

pc2=ax[1].pcolormesh(yearrange,np.arange(0,2),yearcountstart,cmap=cmap2,vmin=0,linewidth=0)
pc2.set_rasterized(True)
ax[1].tick_params(direction='out')

ax[1].set_xticks(np.arange(1880,2016,20))
ax[1].set_xticklabels(np.arange(1880,2016,20))
ax[1].set_yticklabels('')
ax[1].set_ylim([0,1])
ax[1].set_xlim([1880,2016])
ax[1].set_xlabel('year')

ax[1].set_ylabel('Journal start year',rotation=90)
fig.colorbar(pc2,ax=ax[1],ticks=[1,5,10,15])


fig.tight_layout()
#fig.savefig('./figures/fig1bc.eps',dpi=90,format='eps')
#fig.savefig('./figures/fig1bc.svg')
#fig.savefig('./figures/fig1bc.png')
fig.savefig('./figures/fig1bc.pdf')
