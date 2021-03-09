import re

# This file consists of functions that helps clean up abstracts with errors found in QC.

# WRapper function that calls all the functions that should be used pre tagging
def cleanup_pretagger_all(text):
    # Add + at the start to make [0] a non-letter
    text = "+" + text
    # Replace ampredand
    text = text.replace("&amp;", "")  # sometimes & is coded as '&amp;'
    text = text.replace("&", "")
    text = text.replace("e.g.", "")
    text = text.replace("i.e.", "")
    text = text.replace("[?]", "")
    text = cleanup_textEndsWithLetters(text)
    #    print(text)
    text = cleanup_latinnames(text)
    #    print(text)

    text = cleanup_sentenceEndsWithEtc(text)
    text = cleanup_removeGenes(text)
    text = cleanup_removeDecimalNumbers(text)
    #    print(text)
    #    print(text)
    text = cleanup_replaceHyphens(text)
    #    print(text)
    text = cleanup_removeAbrevs(text)
    #    print(text)
    text = cleanup_oneLetterWords(text)
    #    print(text)
    text = cleanup_sentenceEndsInNumber(text)
    text = cleanup_copyrightSentences(text)
    #    print(text)
    text = cleanup_sentenceWithMissingSpaces(text)
    text = cleanup_removeOneWordSentences(text)
    #    print(text)
    text = cleanup_addSpaceAfterPeriod(text)
    text = cleanup_removeExtraWhiteSpaces(text)
    #    print(text)
    # Remove + at the start (if it is still there - gets removed if the first word was an abbreviation)
    if text[0] == "+":
        text = text[1:]
    return text


def cleanup_posttagger_all(text):
    # Occaionally treetagger can parse strange abbreviations "e. g." as "e" being its own word. Remove these.
    text = cleanup_oneLetterWords(text)
    text = text.replace("replaced-url", "")
    return text


# Correct occrances of "1230. New sentence" as treetagger will remove "1230." not just "1230"
def cleanup_sentenceEndsInNumber(text):
    # Find number occurances this occurs
    restr = re.compile("[0-9]+\. [A-Z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        i = 0
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text[i:])
            # Add a space when this occurs
            text = (
                text[0:i]
                + text[i : i + reinfo.end() - 3]
                + " "
                + text[i + reinfo.end() - 3 :]
            )
            i = i + reinfo.end()
    return text


# Sometimes "C. pylorium" becomes a new sentence. Removes all "C." that is found
def cleanup_latinnames(text):
    # Find number occurances this occurs
    restr = re.compile(" [A-Z]\. [a-z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # Add a space when this occurs
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() - 2 :]
    # Can also sometimes be C.pylorium
    restr = re.compile(" [A-Z]\.[a-z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # Remove C.
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() - 1 :]
    # Can also sometimes be a. pylorium (note a. Pylorium and aa. Phylorium will not be detected)
    restr = re.compile(" [a-z]\. [a-z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        #    print('fo')
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # Add a space when this occurs
            text = text[0 : reinfo.end() - 3] + text[reinfo.end() - 2 :]
    return text


# Some occurances of word.Word get misinterpreted by treetagger. add a space where there is word.Word and add a space
def cleanup_sentenceWithMissingSpaces(text):
    # Find number occurances this occurs
    restr = re.compile("\W[a-z]+\.[A-Z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        i = 0
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text[i:])
            # Add a space when this occurs
            text = (
                text[0:i]
                + text[i : i + reinfo.end() - 1]
                + " "
                + text[i + reinfo.end() - 1 :]
            )
            i = i + reinfo.end()
    return text


# Revmoves any occurance of ABC-23SDKL abbreviations. Any abbreviation including a lowercase is still kept
# Hyphens are still kept in the funciton, despite in the "pipeline" they are replaced by spaces before (just in case)
def cleanup_removeAbrevs(text):
    # Find number occurances this occurs.
    # Has to be at least two occurances of A- AB A1 to be removed, PIX,
    restr = re.compile("[^A-Za-z0-9_\-][A-Z0-9][A-Z0-9\-]+[a-z]*")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W (modirfied to include hyphen). (e.g. if " NJNJA.", it returns '.')
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() :]
    #    print(text)
    # This string takes care of things like MyPy
    restr = re.compile("[\W][A-Z0-9]*[a-z]+[A-Z0-9\-]+[a-zA-Z0-9\-]*")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W (modirfied to include hyphen). (e.g. if " NJNJA.", it returns '.')
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() :]
    #    print(text)
    # This string removes any remaining numbers
    restr = re.compile("[0-9]+")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            text = text[0 : reinfo.start()] + text[reinfo.end() :]
    #    print(text)
    return text


# Revmoves genes that contain at least 5 AG with optional hyphen in between
def cleanup_removeGenes(text):
    # Find number occurances this occurs.
    # Has to be at least two occurances of A- AB A1 to be removed, PIX,
    restr = re.compile("[AGCT][-]?[AGCT][-]?[AGCT][-]?[AGCT][-]?[AGCT-]+")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W (modirfied to include hyphen). (e.g. if " NJNJA.", it returns '.')
            text = text[0 : reinfo.start()] + text[reinfo.end() :]
    return text


# Revmoves numbers which are seperated by a period (otherwise NN.NN becomes ".)
def cleanup_removeDecimalNumbers(text):
    # Find number occurances this occurs.
    # Has to be at least two occurances of A- AB A1 to be removed, PIX,
    restr = re.compile("[0-9]+\.[0-9]*")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W (modirfied to include hyphen). (e.g. if " NJNJA.", it returns '.')
            text = text[0 : reinfo.start()] + text[reinfo.end() :]
    return text


# All hyphens get replaced with a blankspace. This means all hyphenated words become two. Any abbreviations with hyphens will be treated as two abbreviations
def cleanup_replaceHyphens(text):
    # replace all hyphens
    text = text.replace("-", " ")
    return text


# Correct occuranges when there is a sentence that ends with "etc." and the period marks both the etc and the end of the sentence
def cleanup_sentenceEndsWithEtc(text):
    # Find number occurances this occurs
    restr = re.compile(" etc\. [A-Z]")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # delete the ' etc'
            text = text[0 : reinfo.start()] + text[reinfo.start() + 4 :]
    return text


# sometimes final punctuation is missing which excludes either final sentance or (in short abstract) entire text.
# Also fixes any occuranges where it might be ending in: "words " and adds a period to this as well.
# But in a case where it ends with "words. " , nothing will be added.
def cleanup_textEndsWithLetters(text):
    # Find number occurances this occurs
    restr = re.compile("\w[\w ]*$")
    if restr.search(text):
        text = text + "."
    return text


# Correct occrances of single letters appearing (that are not I, a or A)
def cleanup_oneLetterWords(text):
    # Find number occurances this occurs
    restr = re.compile("\W[bcdefghijklmnopqrstuvwxyzBCDEFGHJKLMNOPQRSTUVWXYZ]\W")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W. (e.g. if " A.", it returns '.')
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() - 1 :]
    return text


# Add extra space after every periods for safety
def cleanup_addSpaceAfterPeriod(text):
    # Find number occurances this occurs
    restr = re.compile("\.")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        i = 0
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text[i:])
            # Add a space when this occurs
            text = (
                text[0:i]
                + text[i : i + reinfo.start() + 1]
                + " "
                + text[i + reinfo.end() :]
            )
            i = i + reinfo.end()
    return text


# Now extra white spaces may exist. Remove these
def cleanup_removeExtraWhiteSpaces(text):
    # Find number occurances this occurs
    restr = re.compile(" [ ]+")
    # Get number of times it occurs
    numberOccurs = restr.findall(text)
    if len(numberOccurs) > 0:
        # Loop through in case there is more than one
        for n in range(0, len(numberOccurs)):
            reinfo = restr.search(text)
            # remove whenever it occurs. leave the second \W. (e.g. if " A.", it returns '.')
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() :]
    return text


# Identifies sentences with one words in them
def cleanup_removeOneWordSentences(text):
    s = 0
    while s == 0:
        restr = re.compile("\. ?[A-Za-z]+ ?\.")
        reinfo = restr.search(text)
        if reinfo == None:
            s = 1
        else:
            # remove whenever it occurs. leave the second \W. (e.g. if " A.", it returns '.')
            text = text[0 : reinfo.start() + 1] + text[reinfo.end() :]
    return text


# Remove copyright related sentences
def cleanup_copyrightSentences(text):
    restr = re.compile("Hum Brain Mapp.*$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile("Copyright.*$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile("[0-9]{4}The Association for the Study of Animal Behaviour.*$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile("VIDEO ABSTRACT\.$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile("\(PsycINFO Database Record\.$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile("\(Funded by.*$")
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    restr = re.compile(
        "This article is protected by copyright\. All rights reserved\.$"
    )
    reinfo = restr.search(text)
    if reinfo != None:
        text = text[0 : reinfo.start()]
    return text


# Conditions for excluding abstract
# - if abstract contains the phase "ABSTRACT TRUNCATED"
def identify_badabstracts(text):
    restr = re.compile("ABSTRACT TRUNCATED")
    restr2 = re.compile("No abstract")
    keep = 1
    if restr.search(text) != None:
        keep = 0
    if restr2.search(text) != None:
        keep = 0
    return keep
