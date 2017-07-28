wdparts <- strsplit(getwd(), '/')[[1]]
rispart <- which(wdparts=='readabilityinscience')
if(length(rispart)==0) stop("Unable to find a 'readabilityinscience' main project
                            folder in current working directory path")
risdir <- paste(wdparts[1:rispart], collapse = '/')
setwd(risdir)

library(ggplot2)
library(feather)
library(tidyverse)
library(viridis)
library(ggthemes)
library(data.table)

# Load Data

noAuthors <- data.table::fread("./data/abstracts/pmids_nrAuthors.csv") %>%
  as.data.frame()

lang <- data.table::fread(input = './data/abstracts/concatenatedLangDataSMALL.csv') %>%
  as.data.frame()


# Merge and Filter

langAuthors <- merge(noAuthors, lang, by = 'pmid', all = F) %>%
  filter(nrAuthors <= 10) %>%
  filter(!is.na(year)) %>%
  filter(year < 2016) %>%
  arrange(nrAuthors) %>%
  select(pmid, nrAuthors, NDC, flesch, year, journalID)

# Ready for Plot

authorPlot <- langAuthors %>%
  mutate(nrAuthors = as.factor(nrAuthors)) %>%
  group_by(nrAuthors, year) %>%
  summarise(
    Flesch = mean(flesch),
    NDC = mean(NDC),
    n = length(flesch)
  )


# Output csv

write.csv(authorPlot, './data/abstracts/nrAuthors_Flesch_NDC.csv', row.names = F)



# Make Violin Plots

Flesch_violin <- ggplot(authorPlot, aes(x=nrAuthors, y=Flesch)) +
  geom_violin(alpha=0.5, aes(fill=nrAuthors, colour=nrAuthors)) +
  stat_summary(fun.y=median, geom="point", size=1.5, color="black", shape=21) +
  ggthemes::theme_base() +
  xlab("Number of Authors") + ylab('Readability (FRE)') +
  theme(legend.position="none")

NDC_violin <- ggplot(authorPlot, aes(x=nrAuthors, y=NDC)) +
  geom_violin(alpha=0.5, aes(fill=nrAuthors, colour=nrAuthors)) +
  stat_summary(fun.y=median, geom="point", size=1.5, color="black", shape=21) +
  ggthemes::theme_base() +
  xlab("Number of Authors") + ylab('Readability (NDC)') +
  theme(legend.position="none")


# Save Violin Plots

ggsave('./figures/fig5b.svg', Flesch_violin, height = 145, width = 302, units = 'mm')

ggsave('./figures/fig5b_SUPPL.svg', NDC_violin, height = 145, width = 302, units = 'mm')
