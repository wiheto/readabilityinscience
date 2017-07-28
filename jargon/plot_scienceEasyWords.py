import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import scipy.stats as sps

# This script plots the main figure for the jargon analysis (fig 5a). Also calculates the Pearson correlation and confidence intervals.

easywords=pd.read_json('./jargon/lang_generalsciencejargon.json')
easywords.reset_index()

datavg = easywords.groupby(easywords.year).mean()
datavg['year']=datavg.index

fig,ax = plt.subplots(1,1)
ax.scatter(datavg.year, datavg.classic2949, color='k')
ax.scatter(datavg.year, datavg.generalScienceJargon, data=datavg, color='r')
ax.grid(True)
ax.set_xlim([1880,2020])

fig.savefig('./jargon/easywords_pruned.pdf')

fig,ax = plt.subplots(1,1)
ax.scatter(datavg.year, datavg.classic2949, color='k')
ax.scatter(datavg.year, datavg.science2949, data=datavg, color='g')
ax.grid(True)
ax.set_xlim([1880,2020])

fig.savefig('./jargon/easywords_2949.pdf')

fig,ax = plt.subplots(1,1)
ax.scatter(datavg.year, datavg.classic2949, color='k')
ax.scatter(datavg.year, datavg.generalScienceJargon, data=datavg, color='r')
ax.scatter(datavg.year, datavg.science2949, data=datavg, color='g')
ax.grid(True)
ax.set_xlim([1880,2020])
fig.savefig('./jargon/easywords_combined.pdf')
fig.savefig('./figures/fig6a.pdf')
fig.savefig('./figures/fig6a.png')


rc=sps.pearsonr(datavg.year,datavg.classic2949)
rj=sps.pearsonr(datavg.year,datavg.generalScienceJargon)
rs=sps.pearsonr(datavg.year,datavg.science2949)

# Print confidence intervals
n=len(datavg.year)
def CI(r,n):
    z = np.arctanh(r)
    standard_error = 1/np.sqrt(n-3)
    ci = z + np.array([-1,1]) * standard_error * sps.norm.pdf((1+0.95)/2)
    return np.tanh(ci)

print(CI(rc[0],n))
print(CI(rs[0],n))
print(CI(rj[0],n))
