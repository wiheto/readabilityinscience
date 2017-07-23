###############################################################################################################
#  Implementation of stats model for FRE and NDC scores vs. year and FRE, NDC vs. number of authors and year  #
###############################################################################################################


#####################
# Setting correct working directory & Library imports
#####################

wdparts <- strsplit(getwd(), '/')[[1]]
rispart <- which(wdparts=='readabilityinscience')
if(length(rispart)==0) stop("Unable to find a 'readabilityinscience' main project
                            folder in current working directory path")
risdir <- paste(wdparts[1:rispart], collapse = '/')
setwd(risdir)

library(lme4)
library(lmerTest)
library(ggplot2)
library(plyr)
library(sjPlot)
library(feather)
library(knitr)
library(data.table)


#####################
# Data wrangling
#####################

# Read in concatenated lang data and number of authors from csvs
# This assumes both the concatenated data and number of authors csvs are in the data/abstracts/ folder
df_concat <- data.table::fread('./data/abstracts/concatenatedLangDataSMALL.csv')

csv_nrauthors <- data.table::fread('./data/abstracts/pmids_nrAuthors.csv')
csv_nrauthors$pmid <- as.numeric(csv_nrauthors$pmid)

# Put number of authors in main data frame
df_main <- merge(df_concat, csv_nrauthors, by = "pmid", all.x = TRUE)

# Get column names of loaded data
colnames(df_main)

# How many NAs are there in authors?
sum(is.na(df_main$nrAuthors))

# Drop doi as it is not needed further
df_main <- subset(df_main, select = -c(doi))

# Code journalID as factor instead of integer
df_main$journalID <- as.factor(df_main$journalID)

# Drop rows with year 2016 (and younger)
df_main <- df_main[!df_main$year > 2015,] 

# Drop NaNs 
df_main <- df_main[!is.na(df_main$flesch),]
df_main <- df_main[!is.na(df_main$NDC),]

# Center year (but don't scale by SD)
df_main$year.c <- scale(df_main$year, scale=F)


#####################
# Descriptives
#####################

# Overview of articles per journal and per year
table(df_main$journalID)
table(df_main$year)
table(df_main$year[df_main$year > 1990], df_main$journalID[df_main$year > 1990])

# Number of abstracts that we analyze
nrow(df_main)

# Number of unique journals
length(unique(df_main$journalID))


#####################
# Plots
#####################

# Flesch by year over all articles
ggplot(df_main, aes(x = year, y = flesch)) +
        stat_summary(fun.data = mean_se, geom = "ribbon",
                     color = NA, alpha = 0.3) +
        stat_summary(fun.y = mean, geom = "line") +
        theme_bw(base_size = 10) +
        labs(y = "Flesch score",
             x = "Year")

# Histograms per journal
ggplot(df_main, aes(x = flesch)) +
        geom_histogram(fill = "gray28", binwidth = 1) +
        facet_wrap("journalID", scales = "free_y")

# Histograms per year
ggplot(df_main, aes(x = flesch)) +
        geom_histogram(fill = "gray28", binwidth = 10) +
        facet_wrap("year", scales = "free_y")


#####################
# Stats - Linear Mixed Model: 
# Model every individual article over years
#####################

##########
# FRE
##########

# journals as random effects (intercepts): null-model
mod_flesch_journalRX_i <- lmer(flesch ~ 1 + (1 | journalID), data = df_main, REML = FALSE)
summary(mod_flesch_journalRX_i)

aic_mod_flesch_journalRX_i <- AIC(mod_flesch_journalRX_i)
bic_mod_flesch_journalRX_i <- BIC(mod_flesch_journalRX_i)

# journals as random effects (intercepts), year as IV
mod_flesch_yearFX_journalRX_i <- lmer(flesch ~ year.c + (1 | journalID), data = df_main, REML = FALSE)
summary_mod_flesch_yearFX_journalRX_i <- summary(mod_flesch_yearFX_journalRX_i)

aic_mod_flesch_yearFX_journalRX_i <- AIC(mod_flesch_yearFX_journalRX_i)
bic_mod_flesch_yearFX_journalRX_i <- BIC(mod_flesch_yearFX_journalRX_i)
beta_mod_flesch_yearFX_journalRX_i <- as.numeric(summary_mod_flesch_yearFX_journalRX_i$coefficients[,"Estimate"][2])
se_mod_flesch_yearFX_journalRX_i <- as.numeric(summary_mod_flesch_yearFX_journalRX_i$coefficients[,"Std. Error"][2])
t_mod_flesch_yearFX_journalRX_i <- as.numeric(summary_mod_flesch_yearFX_journalRX_i$coefficients[,"t value"][2])
df_mod_flesch_yearFX_journalRX_i <- as.numeric(summary_mod_flesch_yearFX_journalRX_i$coefficients[,"df"][2])
p_mod_flesch_yearFX_journalRX_i <- as.numeric(summary_mod_flesch_yearFX_journalRX_i$coefficients[,"Pr(>|t|)"][2])
CI95_lb_mod_flesch_yearFX_journalRX_i <-  beta_mod_flesch_yearFX_journalRX_i-1.96*se_mod_flesch_yearFX_journalRX_i
CI95_ub_mod_flesch_yearFX_journalRX_i <-  beta_mod_flesch_yearFX_journalRX_i+1.96*se_mod_flesch_yearFX_journalRX_i

# journals as random effects (intercepts + slopes)
mod_flesch_yearFX_journalRX_is <- lmer(flesch ~ year.c + (year.c | journalID), data = df_main, REML = FALSE)
summary_mod_flesch_yearFX_journalRX_is <- summary(mod_flesch_yearFX_journalRX_is)

# Save FRE LME model output
save(list = c("mod_flesch_yearFX_journalRX_is"), file = './data/LME_models/mod_flesch_yearFX_journalRX_is.Rda')

aic_mod_flesch_yearFX_journalRX_is <- AIC(mod_flesch_yearFX_journalRX_is)
bic_mod_flesch_yearFX_journalRX_is <- BIC(mod_flesch_yearFX_journalRX_is)
beta_mod_flesch_yearFX_journalRX_is <- as.numeric(summary_mod_flesch_yearFX_journalRX_is$coefficients[,"Estimate"][2])
se_mod_flesch_yearFX_journalRX_is <- as.numeric(summary_mod_flesch_yearFX_journalRX_is$coefficients[,"Std. Error"][2])
t_mod_flesch_yearFX_journalRX_is <- as.numeric(summary_mod_flesch_yearFX_journalRX_is$coefficients[,"t value"][2])
df_mod_flesch_yearFX_journalRX_is <- as.numeric(summary_mod_flesch_yearFX_journalRX_is$coefficients[,"df"][2])
p_mod_flesch_yearFX_journalRX_is <- as.numeric(summary_mod_flesch_yearFX_journalRX_is$coefficients[,"Pr(>|t|)"][2])
CI95_lb_mod_flesch_yearFX_journalRX_is <-  beta_mod_flesch_yearFX_journalRX_is-1.96*se_mod_flesch_yearFX_journalRX_is
CI95_ub_mod_flesch_yearFX_journalRX_is <-  beta_mod_flesch_yearFX_journalRX_is+1.96*se_mod_flesch_yearFX_journalRX_is

# Some diagnostic plots
sjp.lmer(mod_flesch_yearFX_journalRX_is, sort.est = "year.c", y.offset = .4)
sjp.lmer(mod_flesch_yearFX_journalRX_is, type = "rs.ri")
sjp.lmer(mod_flesch_yearFX_journalRX_is, type = "re.qq")

# Make output table for main models
df_output_flesch <- data.frame(dAIC = c(aic_mod_flesch_journalRX_i - aic_mod_flesch_yearFX_journalRX_is, aic_mod_flesch_yearFX_journalRX_i - aic_mod_flesch_yearFX_journalRX_is, NA),
                               dBIC = c(bic_mod_flesch_journalRX_i - bic_mod_flesch_yearFX_journalRX_is, bic_mod_flesch_yearFX_journalRX_i - bic_mod_flesch_yearFX_journalRX_is, NA),
                               beta = c(NA, beta_mod_flesch_yearFX_journalRX_i, beta_mod_flesch_yearFX_journalRX_is),
                               se = c(NA, se_mod_flesch_yearFX_journalRX_i, se_mod_flesch_yearFX_journalRX_is),
                               CI95.lb = c(NA,CI95_lb_mod_flesch_yearFX_journalRX_i,CI95_lb_mod_flesch_yearFX_journalRX_is),
                               CI95.ub = c(NA,CI95_ub_mod_flesch_yearFX_journalRX_i,CI95_ub_mod_flesch_yearFX_journalRX_is),
                               t = c(NA, t_mod_flesch_yearFX_journalRX_i, t_mod_flesch_yearFX_journalRX_is),
                               df = c(NA,df_mod_flesch_yearFX_journalRX_i,df_mod_flesch_yearFX_journalRX_is),
                               p = c(NA, p_mod_flesch_yearFX_journalRX_i, p_mod_flesch_yearFX_journalRX_is))


############################
# Adding number of authors
############################

# All articles with data regarding number of authors 
mod_flesch_yearFX_nrAuthorsFX_journalRX_is <- lmer(flesch ~ year.c + nrAuthors + (year.c | journalID), data = df_main, REML = FALSE)
summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is <- summary(mod_flesch_yearFX_nrAuthorsFX_journalRX_is)

# Diagnostics
relgrad <- with(mod_flesch_yearFX_nrAuthorsFX_journalRX_is@optinfo$derivs,solve(Hessian,gradient))
max(abs(relgrad))

# Number of authors limited to 10
mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10 <- lmer(flesch ~ year.c + nrAuthors + (year.c | journalID), data = df_main[df_main$nrAuthors<=10,], REML = FALSE)
summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10 <- summary(mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10)

# Make output table for authors Flesch

# Make 95% CI for year predictor
beta_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][2]),
              as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][2]))
se_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][2]),
            as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][2]))

CI.lb.year <- beta_year - se_year*1.96
CI.ub.year <- beta_year + se_year*1.96

# Make 95% CI for nrAuthors predictor
beta_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][3]),
                 as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][3]))
se_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][3]),
               as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][3]))

CI.lb.authors <- beta_authors - se_authors*1.96
CI.ub.authors <- beta_authors + se_authors*1.96

df_output_flesch_authors <- data.frame(n = c(nrow(na.omit(df_main[df_main$nrAuthors<=10,])),length(na.omit(df_main$nrAuthors))),
                                       beta_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][2]),
                                                     as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][2])),
                                       se_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][2]),
                                                   as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][2])),
                                       CI95_year_lb = CI.lb.year,
                                       CI95_year_ub = CI.ub.year,
                                       t_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"t value"][2]),
                                                  as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"t value"][2])),
                                       df_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"df"][2]),
                                                   as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"df"][2])),
                                       p_year = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Pr(>|t|)"][2]),
                                                  as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Pr(>|t|)"][2])),
                                       beta_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][3]),
                                                        as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][3])),
                                       se_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][3]),
                                                      as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][3])),
                                       CI95_lb_authors = CI.lb.authors,
                                       CI95_ub_authors = CI.ub.authors,
                                       t_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"t value"][3]),
                                                     as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"t value"][3])),
                                       df_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"df"][3]),
                                                      as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"df"][3])),
                                       p_authors = c(as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Pr(>|t|)"][3]),
                                                     as.numeric(summary_mod_flesch_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Pr(>|t|)"][3])))


##########
# NDC
##########

# journals as random effects (intercepts)
mod_NDC_journalRX_i <- lmer(NDC ~ 1 + (1 | journalID), data = df_main, REML = FALSE)
summary_mod_NDC_journalRX_i <- summary(mod_NDC_journalRX_i)

aic_mod_NDC_journalRX_i <- AIC(mod_NDC_journalRX_i)
bic_mod_NDC_journalRX_i <- BIC(mod_NDC_journalRX_i)

# journals as random effects (intercepts), year as IV
mod_NDC_yearFX_journalRX_i <- lmer(NDC ~ year.c + (1 | journalID), data = df_main, REML = FALSE)
summary_mod_NDC_yearFX_journalRX_i <- summary(mod_NDC_yearFX_journalRX_i)

aic_mod_NDC_yearFX_journalRX_i <- AIC(mod_NDC_yearFX_journalRX_i)
bic_mod_NDC_yearFX_journalRX_i <- BIC(mod_NDC_yearFX_journalRX_i)
beta_mod_NDC_yearFX_journalRX_i <- as.numeric(summary_mod_NDC_yearFX_journalRX_i$coefficients[,"Estimate"][2])
se_mod_NDC_yearFX_journalRX_i <- as.numeric(summary_mod_NDC_yearFX_journalRX_i$coefficients[,"Std. Error"][2])
t_mod_NDC_yearFX_journalRX_i <- as.numeric(summary_mod_NDC_yearFX_journalRX_i$coefficients[,"t value"][2])
df_mod_NDC_yearFX_journalRX_i <- as.numeric(summary_mod_NDC_yearFX_journalRX_i$coefficients[,"df"][2])
p_mod_NDC_yearFX_journalRX_i <- as.numeric(summary_mod_NDC_yearFX_journalRX_i$coefficients[,"Pr(>|t|)"][2])
CI95_lb_mod_NDC_yearFX_journalRX_i <-  beta_mod_NDC_yearFX_journalRX_i-1.96*se_mod_NDC_yearFX_journalRX_i
CI95_ub_mod_NDC_yearFX_journalRX_i <-  beta_mod_NDC_yearFX_journalRX_i+1.96*se_mod_NDC_yearFX_journalRX_i

# journals as random effects (intercepts + slopes)
mod_NDC_yearFX_journalRX_is <- lmer(NDC ~ year.c + (year.c | journalID), data = df_main, REML = FALSE)
summary_mod_NDC_yearFX_journalRX_is <- summary(mod_NDC_yearFX_journalRX_is)

# Save NDC LME model output
save(list=c("mod_NDC_yearFX_journalRX_is"), file="./data/LME_models/mod_NDC_yearFX_journalRX_is.Rda")

# Diagnostics
relgrad <- with(mod_NDC_yearFX_journalRX_is@optinfo$derivs, solve(Hessian,gradient))
max(abs(relgrad))

aic_mod_NDC_yearFX_journalRX_is <- AIC(mod_NDC_yearFX_journalRX_is)
bic_mod_NDC_yearFX_journalRX_is <- BIC(mod_NDC_yearFX_journalRX_is)
beta_mod_NDC_yearFX_journalRX_is <- as.numeric(summary_mod_NDC_yearFX_journalRX_is$coefficients[,"Estimate"][2])
se_mod_NDC_yearFX_journalRX_is <- as.numeric(summary_mod_NDC_yearFX_journalRX_is$coefficients[,"Std. Error"][2])
t_mod_NDC_yearFX_journalRX_is <- as.numeric(summary_mod_NDC_yearFX_journalRX_is$coefficients[,"t value"][2])
df_mod_NDC_yearFX_journalRX_is <- as.numeric(summary_mod_NDC_yearFX_journalRX_is$coefficients[,"df"][2])
p_mod_NDC_yearFX_journalRX_is <- as.numeric(summary_mod_NDC_yearFX_journalRX_is$coefficients[,"Pr(>|t|)"][2])
CI95_lb_mod_NDC_yearFX_journalRX_is <-  beta_mod_NDC_yearFX_journalRX_is-1.96*se_mod_NDC_yearFX_journalRX_is
CI95_ub_mod_NDC_yearFX_journalRX_is <-  beta_mod_NDC_yearFX_journalRX_is+1.96*se_mod_NDC_yearFX_journalRX_is

df_output_NDC <- data.frame(dAIC = c(aic_mod_NDC_journalRX_i - aic_mod_NDC_yearFX_journalRX_is, aic_mod_NDC_yearFX_journalRX_i - aic_mod_NDC_yearFX_journalRX_is, NA),
                            dBIC = c(bic_mod_NDC_journalRX_i - bic_mod_NDC_yearFX_journalRX_is, bic_mod_NDC_yearFX_journalRX_i - bic_mod_NDC_yearFX_journalRX_is, NA),
                            beta = c(NA, beta_mod_NDC_yearFX_journalRX_i, beta_mod_NDC_yearFX_journalRX_is),
                            se = c(NA, se_mod_NDC_yearFX_journalRX_i, se_mod_NDC_yearFX_journalRX_is),
                            CI95.lb = c(NA,CI95_lb_mod_NDC_yearFX_journalRX_i,CI95_lb_mod_NDC_yearFX_journalRX_is),
                            CI95.ub = c(NA,CI95_ub_mod_NDC_yearFX_journalRX_i,CI95_ub_mod_NDC_yearFX_journalRX_is),
                            t = c(NA, t_mod_NDC_yearFX_journalRX_i, t_mod_NDC_yearFX_journalRX_is),
                            df = c(NA, df_mod_NDC_yearFX_journalRX_i, df_mod_NDC_yearFX_journalRX_is),
                            p = c(NA, p_mod_NDC_yearFX_journalRX_i, p_mod_NDC_yearFX_journalRX_is))

############################
# Adding number of authors
############################

mod_NDC_yearFX_nrAuthorsFX_journalRX_is <- lmer(NDC ~ year.c + nrAuthors + (year.c | journalID), data = df_main, REML = FALSE)
summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is <- summary(mod_NDC_yearFX_nrAuthorsFX_journalRX_is)

# Diagnostics
relgrad <- with(mod_NDC_yearFX_nrAuthorsFX_journalRX_is@optinfo$derivs, solve(Hessian,gradient))
max(abs(relgrad))

# Number of authors capped at 10
mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10 <- lmer(NDC ~ year.c + nrAuthors + (year.c | journalID), data = df_main[df_main$nrAuthors<=10,], REML = FALSE)
summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10 <- summary(mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10)

# Make 95% CI for year predictor
beta_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][2]),
              as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][2]))
se_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][2]),
            as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][2]))

CI.lb.year <- beta_year - se_year*1.96
CI.ub.year <- beta_year + se_year*1.96

# Make 95% CI for nrAuthors predictor
beta_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][3]),
                 as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][3]))
se_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][3]),
               as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][3]))

CI.lb.authors <- beta_authors - se_authors*1.96
CI.ub.authors <- beta_authors + se_authors*1.96

# Make output table for authors NDC
df_output_NDC_authors <- data.frame(n = c(length(na.omit(df_main$nrAuthors[df_main$nrAuthors<=10])), length(na.omit(df_main$nrAuthors))),
                                    beta_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][2]),
                                                  as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][2])),
                                    se_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][2]),
                                                as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][2])),
                                    CI95_year_lb = CI.lb.year,
                                    CI95_year_ub = CI.ub.year,
                                    t_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"t value"][2]),
                                               as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"t value"][2])),
                                    df_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"df"][2]),
                                                as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"df"][2])),
                                    p_year = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Pr(>|t|)"][2]),
                                               as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Pr(>|t|)"][2])),
                                    beta_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Estimate"][3]),
                                                     as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Estimate"][3])),
                                    se_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Std. Error"][3]),
                                                   as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Std. Error"][3])),
                                    CI95_lb_authors = CI.lb.authors,
                                    CI95_ub_authors = CI.ub.authors,
                                    t_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"t value"][3]),
                                                  as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"t value"][3])),
                                    df_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"df"][3]),
                                                   as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"df"][3])),
                                    p_authors = c(as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is_10$coefficients[,"Pr(>|t|)"][3]),
                                                  as.numeric(summary_mod_NDC_yearFX_nrAuthorsFX_journalRX_is$coefficients[,"Pr(>|t|)"][3])))


### Main results table

df_output_master <- rbind(df_output_flesch, df_output_NDC)

Model.ID <- rep(c("M0", "M1", "M2"), 2)
Metric.ID <- c("FRE", "", "", "NDC", "", "")

df_output_master_s1 <- cbind(Metric.ID, Model.ID, df_output_master)

knitr::kable(df_output_master_s1, digits=c(0,0,0,0,3,3,3,3,2,0))


### Number of authors results table

Metric.ID <- c("FRE", "", "NDC", "")

df_output_master_s2 <- cbind(Metric.ID, rbind(df_output_flesch_authors, df_output_NDC_authors))

knitr::kable(df_output_master_s2, digits=c(0,0,3,3,3,3,2,0,0,3,3,3,3,2,0,0))