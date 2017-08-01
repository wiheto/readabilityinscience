#########################################################################
#         Plotting script (Fig. 4b + Supplementaries to Fig. 4)         #
#########################################################################

#####################################
# Libraries and initialization
#####################################

# Clear workspace
rm(list = ls())

# Set working directory to main folder in repo
wdparts <- strsplit(getwd(), '/')[[1]]
rispart <- which(wdparts=='readabilityinscience')
if(length(rispart)==0) stop("Unable to find a 'readabilityinscience' main project
                            folder in current working directory path")
risdir <- paste(wdparts[1:rispart], collapse = '/')
setwd(risdir)

library(MASS)
library(RColorBrewer)
library(ggplot2)
library(viridis)

# Read in helper scripts
source('./functions/smoothScatter_densout.R')
source('./functions/percdata_lim.R')

# If the dataframe which is produced by the Python script is present, load that one, otherwise load the
# supplied fulltext data .csv (duplicates already removed)

if(file.exists('./data/fulltexts/stats/all_fulltextabstract_NDC_Flesch_year.csv')) {
        df_full <- read.csv('./data/fulltexts/stats/all_fulltextabstract_NDC_Flesch_year.csv')
} else {
        df_full <- read.csv('./data/fulltexts/stats/Figure4_SourceData1.csv')
}

# Rename columns
colnames(df_full) <- c("NDC_abstracts", "NDC_fulltexts", "PercDiffWord_abstracts",
                       "PercDiffWord_fulltexts", "flesch_abstracts",
                       "flesch_fulltexts", "journal", "pmid",
                       "sentenceCount_abstracts", "sentenceCount_fulltexts",
                       "sumSylCount_abstracts", "sumSylCount_fulltexts",
                       "wordCount_abstracts", "wordCount_fulltexts", "year")

# Remove duplicates if any (this is due to duplicate text file inputs, e.g.
# Genome_Biol_2015_Sep_21_16(1)_200.txt and Genome_Biol_2015_Sep_21_16_200)
df_full <- df_full[!duplicated(df_full),]

# If it should be written out
# write.csv(df_full, './data/fulltexts/stats/final_fulltextdata_all.csv', quote=FALSE, row.names=FALSE)

#####################################
# Stats
#####################################

# Size of final dataset
length(df_full$flesch_abstracts)

# Size of final dataset per journal
length(df_full$flesch_abstracts[df_full$journal=="BMC_Biol"])
length(df_full$flesch_abstracts[df_full$journal=="eLife"])
length(df_full$flesch_abstracts[df_full$journal=="Genome_Biol"])
length(df_full$flesch_abstracts[df_full$journal=="PLoS_Biol"])
length(df_full$flesch_abstracts[df_full$journal=="PLoS_Med"])
length(df_full$flesch_abstracts[df_full$journal=="PLoS_ONE"])

# First and last year of journals
min(df_full$year[df_full$journal=="BMC_Biol"])
min(df_full$year[df_full$journal=="eLife"])
min(df_full$year[df_full$journal=="Genome_Biol"])
min(df_full$year[df_full$journal=="PLoS_Biol"])
min(df_full$year[df_full$journal=="PLoS_Med"])
min(df_full$year[df_full$journal=="PLoS_ONE"])

max(df_full$year[df_full$journal=="BMC_Biol"])
max(df_full$year[df_full$journal=="eLife"])
max(df_full$year[df_full$journal=="Genome_Biol"])
max(df_full$year[df_full$journal=="PLoS_Biol"])
max(df_full$year[df_full$journal=="PLoS_Med"])
max(df_full$year[df_full$journal=="PLoS_ONE"])

# Overall correlations
cor.test(df_full$flesch_abstracts, df_full$flesch_fulltexts, method = "pearson")
cor.test(df_full$NDC_abstracts, df_full$NDC_fulltexts, method = "pearson")

# Journal specific correlations
cor.test(df_full$flesch_abstracts[df_full$journal=="BMC_Biol"],
         df_full$flesch_fulltexts[df_full$journal=="BMC_Biol"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="BMC_Biol"],
         df_full$NDC_fulltexts[df_full$journal=="BMC_Biol"], method = "pearson")

cor.test(df_full$flesch_abstracts[df_full$journal=="eLife"],
         df_full$flesch_fulltexts[df_full$journal=="eLife"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="eLife"],
         df_full$NDC_fulltexts[df_full$journal=="eLife"], method = "pearson")

cor.test(df_full$flesch_abstracts[df_full$journal=="Genome_Biol"],
         df_full$flesch_fulltexts[df_full$journal=="Genome_Biol"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="Genome_Biol"],
         df_full$NDC_fulltexts[df_full$journal=="Genome_Biol"], method = "pearson")

cor.test(df_full$flesch_abstracts[df_full$journal=="PLoS_Biol"],
         df_full$flesch_fulltexts[df_full$journal=="PLoS_Biol"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="PLoS_Biol"],
         df_full$NDC_fulltexts[df_full$journal=="PLoS_Biol"], method = "pearson")

cor.test(df_full$flesch_abstracts[df_full$journal=="PLoS_Med"],
         df_full$flesch_fulltexts[df_full$journal=="PLoS_Med"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="PLoS_Med"],
         df_full$NDC_fulltexts[df_full$journal=="PLoS_Med"], method = "pearson")

cor.test(df_full$flesch_abstracts[df_full$journal=="PLoS_ONE"],
         df_full$flesch_fulltexts[df_full$journal=="PLoS_ONE"], method = "pearson")
cor.test(df_full$NDC_abstracts[df_full$journal=="PLoS_ONE"],
         df_full$NDC_fulltexts[df_full$journal=="PLoS_ONE"], method = "pearson")


#####################################
# Fig. 4b (FRE)
#####################################

setwd(paste0(getwd(), '/figures'))

# Set minimum axis limits to 99% of the data
limits_flesch <- percdata_lim(df_full$flesch_abstracts,
                              df_full$flesch_fulltexts, ylo.start = -20,
                              yhi.start = 50, xlo.start = -30, xhi.start = 50,
                              perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts ~ df_full$flesch_abstracts)

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts, df_full$flesch_fulltexts, nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap <- 200 # Use a value slightly above densout$max for both Flesch and NDC

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg('fig4b.svg', width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts, df_full$flesch_fulltexts, nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# Colour bar for both Flesch (max ~ 165) and NDC (max ~ 175) until 200

abslabels <- c(0, 1, 10, colourcap)
positions <- (abslabels)^0.25
labels <- abslabels

my.colors <- colorRampPalette(viridis::viridis(n = 1000, option = 'inferno'))
z <- matrix(1:100, nrow=1)
x <- 1
y <- seq(0,colourcap^0.25, len=100)

svg('colourbar_fig4_and_suppl.svg', width = 2, height = 7, antialias = c("gray"))
image(x,y,z,col = my.colors(100), axes=FALSE, xlab="", ylab="", useRaster = T)
axis(2, at = positions, labels = labels)
dev.off()


#####################################
# Fig. 4 SUPPL1 (NDC)
#####################################

limits_NDC <- percdata_lim(df_full$NDC_abstracts, df_full$NDC_fulltexts, ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts ~ df_full$NDC_abstracts)

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts, df_full$NDC_fulltexts, nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg('fig4_suppl1.svg', width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts, df_full$NDC_fulltexts, nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

# Most of the density lies in the middle
length(df_full$NDC_fulltexts[df_full$NDC_abstracts<14 & df_full$NDC_abstracts>11])


#####################################
# Fig. for individual journals (Fig. 4 SUPPL2)
#####################################

#####################################
# BMC Biology
#####################################

journal <- "BMC_Biol"

limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -30, xhi.start = 50, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

colourcap <- 200

(densout_NDC$min)
(densout_NDC$max)
colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

#####################################
# eLife
#####################################

journal <- "eLife"

# Flesch

limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -50, xhi.start = 65, perc = 99)

# Manual fixing of the limits outside these minimum boundaries, slightly adjusted for eLife
limits_flesch$xlim[1] <- -38
limits_flesch$xlim[2] <- 62
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

#####################################
# Genome Biology
#####################################

journal <- "Genome_Biol"

# Flesch

# Slightly adjusted initial thresholds for Genome Biology
limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -35, xhi.start = 60, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 25, xlo.start = 5, xhi.start = 25, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

#####################################
# PLoS Biology
#####################################

journal <- "PLoS_Biol"

# Flesch

limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -30, xhi.start = 50, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

#####################################
# PLoS Medicine
#####################################

journal <- "PLoS_Med"

# Flesch

limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -30, xhi.start = 50, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()

#####################################
# PLoS ONE
#####################################

journal <- "PLoS_ONE"

# Flesch

limits_flesch <- percdata_lim(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], ylo.start = -20, yhi.start = 50, xlo.start = -30, xhi.start = 50, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_flesch$xlim[1] <- -40
limits_flesch$xlim[2] <- 60
limits_flesch$ylim[1] <- -30
limits_flesch$ylim[2] <- 70

# Regression line
abstracts_fulltexts_line_flesch <- lm(df_full$flesch_fulltexts[df_full$journal==journal] ~ df_full$flesch_abstracts[df_full$journal==journal])

### Extract max value for smoothScatter for the colour bar

densout <- smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
                                 colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                 xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts')

(densout$min)
(densout$max)

colourcap^0.25 / (densout$max^0.25)
colourend <- (densout$max^0.25) / colourcap^0.25

# Plot figure with % of colour scale until densout$max on a total scale of colourcap

# SVG

svg(paste0('fig4_suppl2_', journal, '_flesch.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$flesch_abstracts[df_full$journal==journal], df_full$flesch_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_flesch$xlim[1], limits_flesch$xlim[2]), ylim = c(limits_flesch$ylim[1], limits_flesch$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend, option = 'inferno')), nrpoints = 0,
              xlab='Readability (FRE) Abstracts', ylab='Readability (FRE) Fulltexts',
              useRaster = TRUE)
clip(limits_flesch$xlim[1]-3, limits_flesch$xlim[2]+3, limits_flesch$ylim[1], limits_flesch$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_flesch, col="white", lwd=2)
dev.off()

# NDC

limits_NDC <- percdata_lim(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], ylo.start = 5, yhi.start = 20, xlo.start = 5, xhi.start = 20, perc = 99)

# Manual fixing of the limits outside these minimum boundaries
limits_NDC$xlim[1] <- 9.5
limits_NDC$xlim[2] <- 15.6
limits_NDC$ylim[1] <- 9.5
limits_NDC$ylim[2] <- 15.6

# Regression line
abstracts_fulltexts_line_NDC <- lm(df_full$NDC_fulltexts[df_full$journal==journal] ~ df_full$NDC_abstracts[df_full$journal==journal])

densout_NDC <- smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
                                     colramp = colorRampPalette(viridis::viridis(n = 1000, option = 'inferno')), nrpoints = 0,
                                     xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts')

(densout_NDC$min)
(densout_NDC$max)

colourcap^0.25 / (densout_NDC$max^0.25)
colourend_NDC <- (densout_NDC$max^0.25) / colourcap^0.25

# SVG
svg(paste0('fig4_suppl2_', journal, '_NDC.svg'), width = 7, height = 7, antialias = c("gray"))
smoothScatter_densout(df_full$NDC_abstracts[df_full$journal==journal], df_full$NDC_fulltexts[df_full$journal==journal], nbin = 128, xlim = c(limits_NDC$xlim[1], limits_NDC$xlim[2]), ylim = c(limits_NDC$ylim[1], limits_NDC$ylim[2]),
              colramp = colorRampPalette(viridis::viridis(n = 1000, end = colourend_NDC, option = 'inferno')), nrpoints = 0,
              xlab='Readability (NDC) Abstracts', ylab='Readability (NDC) Fulltexts',
              useRaster = TRUE)
clip(limits_NDC$xlim[1]-0.19, limits_NDC$xlim[2]+0.18, limits_NDC$ylim[1], limits_NDC$ylim[2]) # Regression line should not extend beyond image borders
abline(abstracts_fulltexts_line_NDC, col="white", lwd=2)
dev.off()
