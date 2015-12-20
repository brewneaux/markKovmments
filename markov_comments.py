#!/usr/bin/env python

import os
import re
import markovify
from urlparse import urlparse
import argparse
import subprocess
import shutil

valid_extensions = [
    "ADA",
    "ADB",
    "2.ADA",
    "ADS",
    "1.ADA",
    "ASM",
    "S",
    "BAS",
    "BB",
    "BMX",
    "C",
    "CLJ",
    "CLS",
    "COB",
    "CBL",
    "CPP",
    "CC",
    "CXX",
    "C",
    "CBP",
    "CS",
    "CSPROJ",
    "D",
    "DBA",
    "DBPro123",
    "E",
    "EFS",
    "EGT",
    "EL",
    "FOR",
    "FTN",
    "F",
    "F77",
    "F90",
    "FRM",
    "FRX",
    "FTH",
    "GED",
    "GM6",
    "GMD",
    "GMK",
    "GML",
    "GO",
    "H",
    "HPP",
    "HXX",
    "HS",
    "I",
    "INC",
    "JAVA",
    "L",
    "LGT",
    "LISP",
    "M",
    "M",
    "M",
    "M4",
    "ML",
    "N",
    "NB",
    "P",
    "PAS",
    "PP",
    "P",
    "PHP",
    "PHP3",
    "PHP4",
    "PHP5",
    "PHPS",
    "Phtml",
    "PIV",
    "PL",
    "PM",
    "PRG",
    "PRO",
    "POL",
    "PY",
    "R",
    "RED",
    "REDS",
    "RB",
    "RESX",
    "RC",
    "RC2",
    "RKT",
    "RKTL",
    "SCALA",
    "SCI",
    "SCE",
    "SCM",
    "SD7",
    "SKB",
    "SKC",
    "SKD",
    "SKF",
    "SKG",
    "SKI",
    "SKK",
    "SKM",
    "SKO",
    "SKP",
    "SKQ",
    "SKS",
    "SKT",
    "SKZ",
    "SLN",
    "SPIN",
    "STK",
    "SWG",
    "TCL",
    "VAP",
    "VB",
    "VBG",
    "VBP",
    "VIP",
    "VBPROJ",
    "VCPROJ",
    "VDPROJ",
    "XPL",
    "XQ",
    "XSL",
    "Y"
]

def updateSourceList():
    listFile = open(os.path.expanduser('~/repo_list'))
    print "Updating sources..."
    for repo in listFile.readlines():
        getRepo(repo.rstrip())
        print "Repo retrieved, walking..."
        walkCode()
        deleteRepo()

def getRepo(repo):
    isUrl = urlparse(repo)
    print "Getting {}".format(repo)
    if not isUrl.scheme:
        raise ValueError('The inputted url was not actually a url.  stopit.')
    dest = '/var/tmp/clone_tmp'
    shutil.rmtree(dest, ignore_errors=True)
    print ("git clone --depth=1 " + repo + " " + dest)
    if subprocess.call("git clone --depth=1 " + repo + " " + dest, shell=True):
        raise Exception('Git clone failed')

def walkCode():
    global valid_extensions
    filelist = []
    outputFile = os.path.expanduser('~/temp_comment_output')
    
    for dirname, dirnames, filenames in os.walk('/var/tmp/clone_tmp'):
        if '.git' in dirnames or '.git' in dirname:
            next

        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext.upper().replace('.','') in valid_extensions:
                filelist.append(os.path.join(dirname, filename))

    print "Walking {} code files for comments".format(len(filelist))
    for filename in filelist:
        getCommentsFromCode(outputFile, filename)

def getCommentsFromCode(outputFile, filename):
    output = open(outputFile, 'a')
    comment_finder_regex = re.compile('^[ *]+(.+)|[ \\]+(.+)|[ #]+(?!(?:include)|define)(.+)')
    ignore_copyright_regex = re.compile('copyright', re.IGNORECASE)
    just_printed_period = False
    for line in open(filename, 'r').readlines():
        results = comment_finder_regex.match(line)
        if results:
            for grp in results.groups():
                if grp is not None:
                    last_thing_printed = re.sub('[^0-9a-zA-Z-_ ]+', '', grp)
                    if len(last_thing_printed) > 2 and not ignore_copyright_regex.match(last_thing_printed):
                        just_printed_period = False
                        output.write(last_thing_printed)
        if not just_printed_period:
            output.write('. ')
            just_printed_period = True
    output.write("\n")
    output.close()

def deleteRepo():
    shutil.rmtree('/var/tmp/clone_tmp')

def generateChain():
    text = open(os.path.expanduser('~/temp_comment_output')).read()
    mark = markovify.Text(text)
    saved = open(os.path.expanduser('~/markov_db'), 'w')
    saved.write(markovify.Chain.to_json(mark.chain))
    saved.close()
    print mark.make_sentence()

def getSentence():
    chain = open(os.path.expanduser('~/markov_db')).read()
    mark = markovify.Text.from_chain(chain)
    return mark.make_sentence()

def main():
    parser = argparse.ArgumentParser(description='Steal comments from GitHub repos, markov them, and make some cool stuff.')

    parser.add_argument('--update',
        action='store_true',
        help='Update repo list')

    parser.add_argument('--export',
        action='store_true',
        help='Export the markov chain')

    parser.add_argument('--create-sentence',
        action='store_true',
        help='Gets a sentence from the default chain')

    args = parser.parse_args()
    if args.update:
        updateSourceList()
        generateChain()

    if args.create_sentence:
        print getSentence()

if __name__ == "__main__":
    main()
