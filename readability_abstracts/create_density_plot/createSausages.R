wdparts <- strsplit(getwd(), '/')[[1]]
rispart <- which(wdparts=='readabilityinscience')
if(length(rispart)==0) stop("Unable to find a 'readabilityinscience' main project 
                            folder in current working directory path")
risdir <- paste(wdparts[1:rispart], collapse = '/')
setwd(risdir)

library("tidyverse")
source('./functions/heat_yeardens.R')
source('./functions/smoothScatter_densout.R')
source('./functions/percdata_lim.R')

# Folders

lang <- data.table::fread(input = './data/abstracts/concatenatedLangDataSMALL.csv') %>%
  as.data.frame() %>%
  filter(!is.na(year)) %>%
  filter(year < 2016)


# Parameters

lang$avgSyl <- lang$sylCount / lang$wordCount
lang$sentenceLength <- lang$wordCount / lang$sentenceCount


# FRE vs NDC axis limits

limits <- percdata_lim(lang$flesch, lang$NDC, perc = 99, xlo.start = -45, xhi.start = 47, ylo.start = 8, yhi.start = 16)

fre_ndc_line <- lm(lang$NDC ~ lang$flesch)


# FRE vs NDC colour limits

densout <- smoothScatter_densout(lang$flesch, lang$NDC, nbin = 128, xlim = c(limits$xlim[1], limits$xlim[2]), ylim = c(limits$ylim[1], limits$ylim[2]), 
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE)', ylab='Readability (NDC)')

scalemax <- ceiling(densout$max/100)*100
colourend <- (densout$max^0.25) / scalemax^0.25

abslabels <- c(0,1,10,100, scalemax)
positions <- (abslabels)^0.25
labels <- abslabels


# Make the figure svg

svglite::svglite('./figures/fig2cdefgh.svg', width = 9.8, height = 5.5)
par(mfrow=c(2,3), mai=c(0.6, 0.6, 0.2, 0.2))

heat_yeardens(lang$flesch, lang$year, c(-30, 70), c(1880,2015), 128, 'Readability (FRE)')
heat_yeardens(lang$NDC, lang$year, c(9, 16), c(1880,2015), 128, 'Readability (NDC)')
smoothScatter(lang$flesch, lang$NDC, nbin = 128, xlim = c(limits$xlim[1], limits$xlim[2]), ylim = c(limits$ylim[1], limits$ylim[2]), 
              colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno', end=colourend)), nrpoints = 0,
              xlab='Readability (FRE)', ylab='Readability (NDC)',useRaster=T)
abline(fre_ndc_line, col="white", lwd=2)

heat_yeardens(lang$avgSyl, lang$year, c(1.2, 2.5), c(1880,2015), 128, 'Mean Syllables/Word')
heat_yeardens(lang$sentenceLength, lang$year, c(5, 50), c(1880,2015), 128, 'Mean Words/Sentence')
heat_yeardens(lang$PercDiffWord, lang$year, c(25,70), c(1880,2015), 128, 'Difficult Words (%)')

dev.off()


# Make the colour bar svg

svglite::svglite('./figures/fig2e_colbar.svg', width = 8, height = 2.2)

abslabels <- c(0,1,10,100, scalemax)
positions <- (abslabels)^0.25
labels <- abslabels

my.colors = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno'))
z=matrix(1:100,ncol = 1)
y=1
x=seq(0,scalemax^0.25,len=100) 
image(x,y,z,col=my.colors(100),axes=FALSE,xlab="",ylab="", useRaster=T)
axis(1, at = positions, labels = labels)

dev.off()


svglite::svglite('./figures/fig2cdfgh_colbar.svg', width = 8, height = 2.2)

positions <- c(0, 0.5, 1)
labels <- c(0, 0.5, 1)

my.colors = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno'))
z=matrix(1:100,ncol = 1)
y=1
x=seq(0,1,len=100) 
image(x,y,z,col=my.colors(100),axes=FALSE,xlab="",ylab="", useRaster=T)
axis(1, at = positions, labels = labels)

dev.off()