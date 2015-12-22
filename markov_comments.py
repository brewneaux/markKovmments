#!/usr/bin/env python

import os
import re
import markovify
from urlparse import urlparse
import argparse
import subprocess
import shutil
import ConfigParser

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

CLONE_TEMP_LOCATION = '/var/tmp/clone_tmp'
MARKOV_DB_LOCATION = '~/markov_db'
COMMENT_TEMP_LOCATION = '~/temp_comment_output'
REPO_LIST_LOCATION = '~/repo_list'
DEBUG = False

def updateSourceList():
    if os.path.isfile(MARKOV_DB_LOCATION):
        backup = MARKOV_DB_LOCATION + '_bak'
        if os.path.isfile(backup):
            os.remove(backup)
        shutil.move(MARKOV_DB_LOCATION, backup)

    if os.path.isfile(COMMENT_TEMP_LOCATION):
        backup = COMMENT_TEMP_LOCATION + '_bak'
        if os.path.isfile(backup):
            os.remove(backup)
        shutil.move(COMMENT_TEMP_LOCATION, backup)

    listFile = open(os.path.expanduser(REPO_LIST_LOCATION))
    print "Updating sources..."
    for repo in listFile.readlines():
        cont = getRepo(repo.rstrip())
        if cont:
            print "Repo retrieved, walking..."
            walkCode()
            if not DEBUG:
                deleteRepo()
    print "Done updating sources and comment file"

def getRepo(repo):
    isUrl = urlparse(repo)
    if repo.strip() == '':
        return False;
    if not isUrl.scheme:
        raise ValueError('The inputted url was not actually a url.  stopit.')
    print "Getting {}".format(repo)
    dest = os.path.expanduser(CLONE_TEMP_LOCATION)
    shutil.rmtree(dest, ignore_errors=True)
    if subprocess.call("git clone --depth=1 " + repo + " " + dest + ' --quiet', shell=True):
        raise Exception('Git clone failed')
    return True

def walkCode():
    global valid_extensions
    filelist = []
    outputFile = os.path.expanduser(COMMENT_TEMP_LOCATION)

    for dirname, dirnames, filenames in os.walk(CLONE_TEMP_LOCATION):
        if '.git' in dirnames or '.git' in dirname:
            next

        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext.upper().replace('.', '') in valid_extensions:
                filelist.append(os.path.join(dirname, filename))

    print "Walking {} code files for comments".format(len(filelist))
    for filename in filelist:
        getCommentsFromCode(outputFile, filename)

def getCommentsFromCode(outputFile, filename):
    output = open(outputFile, 'a')
    comment_finder_regex = re.compile(r'^(?:\s+#|\s[\\]\s+|(?:\s*[*]+))([^@]*)')
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
    shutil.rmtree(CLONE_TEMP_LOCATION)

def generateChain():
    text = open(os.path.expanduser(COMMENT_TEMP_LOCATION)).read()
    mark = markovify.Text(text)
    saved = open(os.path.expanduser(MARKOV_DB_LOCATION), 'w')
    saved.write(markovify.Chain.to_json(mark.chain))
    saved.close()
    print mark.make_sentence()

def getSentence():
    chain = open(os.path.expanduser(MARKOV_DB_LOCATION)).read()
    mark = markovify.Text.from_chain(chain)
    return mark.make_sentence()

def dumpGlobals():
    print 'Debug = {}'.format(DEBUG)
    print 'CLONE_TEMP_LOCATION = {}'.format(CLONE_TEMP_LOCATION)
    print 'MARKOV_DB_LOCATION = {}'.format(MARKOV_DB_LOCATION)
    print 'COMMENT_TEMP_LOCATION = {}'.format(COMMENT_TEMP_LOCATION)
    print 'REPO_LIST_LOCATION = {}'.format(REPO_LIST_LOCATION)

def main():
    global CLONE_TEMP_LOCATION
    global MARKOV_DB_LOCATION
    global COMMENT_TEMP_LOCATION
    global REPO_LIST_LOCATION
    global DEBUG

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

    parser.add_argument('--debug',
        action='store_true',
        help='Sets debug mode')

    if os.path.isfile('config.ini'):
        Config = ConfigParser.ConfigParser()
        Config.read("config.ini")
        if Config.get('main', 'clone_temp_location'):
            CLONE_TEMP_LOCATION = Config.get('main', 'clone_temp_location')
        if Config.get('main', 'markov_db_location'):
            MARKOV_DB_LOCATION = Config.get('main', 'markov_db_location')
        if Config.get('main', 'comment_temp_location'):
            COMMENT_TEMP_LOCATION = Config.get('main', 'comment_temp_location')
        if Config.get('main', 'repo_list_location'):
            REPO_LIST_LOCATION = Config.get('main', 'repo_list_location')

    args = parser.parse_args()

    if args.debug:
        DEBUG = True
        dumpGlobals()

    if args.update:
        updateSourceList()
        generateChain()

    if args.create_sentence:
        print getSentence()

if __name__ == "__main__":
    main()
