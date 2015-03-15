#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Main program for analyzing the downloaded files.
Python 3 is highly recommended since it handles
unicode better.
"""

# Note to self: Keep this script working with
# both "python" (2.7.x) and "python3"!

__author__ = "Henrik Laban Torstensson, Andreas Söderlund, Timmy Larsson, Niklas Bolmdahl, Drahflow"
__license__ = "MIT"

import argparse
import database
import fnmatch
import multiprocessing
import os
import subprocess
import tempfile
import parser
import random
import signal
import sys
import time
import zipfile
import re
from hashlib import md5
from shutil import rmtree
from collections import defaultdict, deque

if sys.version_info >= (3,):
    from io import BytesIO as FileLike
else:
    from cStringIO import StringIO as FileLike


def typographicAnalyzeWorker(iq, oq):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Processes will receive SIGINT on Ctrl-C in main program. Just ignore it.
    for odtFilename, odtContent in iter(iq.get, "STOP"):
        resDict = {}
        odtFile = FileLike(odtContent) #FileLike provides seek()
        if zipfile.is_zipfile(odtFile):
            try:
                resDict = parser.parser(odtFile)
            except (parser.NumberingException, parser.NoAnswerException) as e:
                resDict["parsingException"] = str(e)
                print("Error parsing {}: {}".format(odtFilename, str(e)))
        else:
            resDict["error"] = "Not a valid zip file"
            print("ERROR: {} is not a valid zip file!".format(odtFilename))
        odtFile.close()

        oq.put(resDict)

def normalizeWord(s):
    return re.sub('[^a-zA-Z0-9äöüÄÖÜß]', '', s)

def parseAnswers(text, questions, index, MATCHLEN):
    answers = defaultdict(deque)

    quesPos = None
    currentyKey = questions[0][0]
    words = text.split()
    nWords = [normalizeWord(w) for w in words]

    def locateInQuestions(pos, valid):
        if pos >= len(nWords) - MATCHLEN: return None

        for i in [i for i in index[nWords[pos]] if valid(i)]:
            found = True
            for j in range(0, MATCHLEN):
                if nWords[pos + j] != questions[i + j][1]:
                    found = False
                    break
            if found: return i + 1
        return None

    for textPos in range(0, len(words)):
        if quesPos is not None:
            if nWords[textPos] == questions[quesPos][1]:
                quesPos = quesPos + 1
            else:
                newPos = locateInQuestions(textPos, lambda i: i >= quesPos + 1)
                if newPos is None:
                    newPos = locateInQuestions(textPos, lambda i: i < quesPos + 1)
                quesPos = newPos
        else:
            quesPos = locateInQuestions(textPos, lambda i: True)

        if quesPos is None or quesPos >= len(questions):
            answers[currentyKey].append(words[textPos])
        else:
            if questions[quesPos][0] != '   ':
                currentyKey = questions[quesPos][0]

    for k in answers.keys():
        # eliminate random footnote numbers
        while answers[k] and re.match("^.?\\d+.?$", answers[k][0]):
            answers[k].popleft()
        while answers[k] and re.match("^.?\\d+.?$", answers[k][-1]):
            answers[k].pop()

        answers[k] = " ".join(answers[k])

    return answers


def textBasedAnalyzeWorker(iq, oq):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Processes will receive SIGINT on Ctrl-C in main program. Just ignore it.

    MATCHLEN = 7

    questions = []
    with open('consultation-document_en.dat', 'r') as consultation:
        for line in consultation:
            key = line[0:3]
            for word in line[3:].split():
                questions.append((key, normalizeWord(word)))

    index = defaultdict(list)
    for i in range(0, len(questions) - MATCHLEN):
        index[questions[i][1]].append(i)

    for filename, content in iter(iq.get, "STOP"):
        tmpname = md5(filename.encode('utf-8')).hexdigest()
        text = ''

        fileending = filename.lower()[-5::]
        if fileending.endswith(".pdf"):
            try:
                with open(tmpname + '.pdf', 'w') as pdf:
                    if sys.version_info >= (3,):
                        pdf.buffer.write(content)
                    else:
                        pdf.write(content)
                # execline = 'unoconv -f odt -o ' + odtTempFileName + ' '+ thisTempFileName
                subprocess.call('pdftotext %s.pdf %s.txt' % (tmpname, tmpname), shell=True)
                with open(tmpname + '.txt', 'r') as txt:
                    text = txt.read()
            finally:
                try:
                    os.remove(tmpname + '.pdf')
                    os.remove(tmpname + '.txt')
                except:
                    pass
        else:
            continue

        answers = parseAnswers(text, questions, index, MATCHLEN)

        print ("%s -------------------------" % (filename))
        print (answers['600'] or "<600 unparsed>")
        print (answers['020'] or "<020 unparsed>")

        oq.put({
            'name': answers['600'],
            'answers': answers,
        })


class ConsultationZipHandler:
    """
    Class analyzing zip files with consultation form responses
    """

    def __init__(self):
        self.categoryDict = {}
        self.count = 0
        self.extensionDict = {}
        self.fileList = []
        self.fileListByZip = {} # zip filename -> list of containing files
        self.languageDict = {}
        self.zipFiles = []      # (filename, ZipFile object)

    def addZip(self, zipFilename):
        """
        Read statistics in zip file
        """

        zipFile = zipfile.ZipFile(zipFilename)
        self.zipFiles.append((zipFilename, zipFile)) # Save in instance list
        self.fileListByZip[zipFilename] = []

        """
        Loop through all files in the zip file
        and count the number of files in different
        categories, with different extensions and
        in different languages
        """
        for filename in zipFile.namelist():
            category = os.path.dirname(filename)
            formName = os.path.basename(filename)
            if formName == "":
                # Directory entry
                continue
            if formName == "Thumbs.db":
                continue
            self.fileList.append(formName)
            self.fileListByZip[zipFilename].append(filename)
            self.count += 1

            # Category
            if category in self.categoryDict.keys():
                self.categoryDict[category]["count"] += 1
            else:
                self.categoryDict[category] = {"count": 1}

            # Extension
            extension = formName.split(".")[-1]
            if extension in self.extensionDict.keys():
                self.extensionDict[extension]["count"] += 1
            else:
                self.extensionDict[extension] = {"count": 1}

            # Language
            languageSplit = ".".join(formName.split(".")[:-1]).split("_") #TODO: Split also on "." and "-"
            if len(languageSplit) == 0:
                language = "??"
            else:
                if len(languageSplit[-1]) < 5:
                    language = languageSplit[-1].lower().strip("-").rstrip(".").lstrip("(").rstrip(")")
                    if len(language) != 2:
                        language = "??"
                else:
                    language = "??"
            if language in (None, ""):
                language = "??"
            if language in self.languageDict.keys():
                self.languageDict[language]["count"] += 1
            else:
                self.languageDict[language] = {"count": 1}

    def analyze(self, handleFile, worker, randomize=False, showProgress=False, printNames=False, numProcesses=1, numberOfFiles=0, queueSize=100, filePattern="*", skip=0, wipeDatabase=False, convert2odt=False):
        if numberOfFiles == 0:
            numOfFilesToAnalyze = self.getCount()
        else:
            numOfFilesToAnalyze = min(self.getCount(), numberOfFiles)
        zipFilenames = [x[0] for x in self.zipFiles]
        if randomize:
            random.shuffle(zipFilenames)

        print("Initializing database...")
        db = database.Database(overwrite=wipeDatabase)
        print("")
        count = 0
        print("Queue size:", queueSize)
        if skip:
            print("Skipping first {} files".format(skip))
        print("Analyzing using {} process(s)...".format(numProcesses))
        inputQueue = multiprocessing.Queue(queueSize)
        resultQueue = multiprocessing.Queue()
        processes = []
        for i in range(numProcesses):
            process = multiprocessing.Process(name="{}".format(i + 1), target=worker, args=[inputQueue, resultQueue])
            process.start()
            processes.append(process)
        startTime = time.time()
        abort = False
        try:
            for (zipFilename, zipFile) in self.zipFiles:
                if abort:
                    break
                filenames = self.fileListByZip[zipFilename]
                if randomize:
                    random.shuffle(filenames)
                if convert2odt:
                    tempdir = tempfile.mkdtemp(prefix="eucrcon-")
                for filename in filter(lambda x: fnmatch.fnmatch(x.lower(), filePattern), filenames):
                    if skip:
                        skip -= 1
                        continue
                    if numberOfFiles and count >= numberOfFiles:
                        print("Aborting after enqueuing {} files".format(numberOfFiles))
                        abort = True
                        break

                    if printNames:
                        print("Handling {}...".format(filename))

                    handleFile(inputQueue, zipFile, filename)

                    count += 1
                    if showProgress:
                        if count % showProgress == 0:
                            print("{:.2%} enqueued ({}/{})".format(float(count) / float(numOfFilesToAnalyze), count, numOfFilesToAnalyze))
        except KeyboardInterrupt:
            print("  Aborting")
        print("Waiting for files in queue to be analyzed...")
        for i in range(numProcesses):
            inputQueue.put("STOP")
        results = []
        print("Fetching {} results from result queue...".format(count))
        for i in range(count): # There must be exactly this number of dictionaries in the result queue
            results.append(resultQueue.get())
        for process in processes:
            process.join()
        print("{:.2%} analyzed ({}/{})".format(float(count) / float(numOfFilesToAnalyze), count, numOfFilesToAnalyze))
        duration = time.time() - startTime
        if count > 0:
            print("{} files analyzed in {:.1f} s (avg {:.3f} s)".format(count, duration, duration/count))
        exceptionList = list(filter(lambda x: "parsingException" in x.keys(), results))
        nbrOfParsingExceptions = len(exceptionList)
        print("{} exceptions in {} files ({:.2%})".format(nbrOfParsingExceptions, count, float(nbrOfParsingExceptions) / float(count)))
        print("")
        print("Inserting into database...")
        for resDict in results:
            if not "answers" in resDict.keys():
                continue
            formId = db.putForm(resDict["name"], resDict["type"], "")
            for (questionNbr, answer) in enumerate(resDict["answers"], start=1):
                db.putAnswer(formId, questionNbr, answer[0], answer[1])
        print("Committing to disk...")
        db.save()
        if convert2odt and "eucrcon" in tempdir:
            rmtree(tempdir)

    def convertFiles(self, tempdir, zipFile, filename, inputQueue, extension):
        thisTempFile, thisTempFileName = tempfile.mkstemp(dir=tempdir)
        #thisTempFile.close()
        newFilename = thisTempFileName + extension
        os.rename(thisTempFileName, newFilename)
        thisTempFileName = newFilename
        thisTempFile = open(thisTempFileName,'w')
        odtTempFileName = thisTempFileName + '.odt'
        thisTempFile.write(zipFile.read(filename))
        thisTempFile.close()
        # print(odtTempFileName)
        # print(thisTempFileName)
        execline = 'unoconv -f odt -o ' + odtTempFileName + ' '+ thisTempFileName
        print(execline)
        subprocess.call(execline, shell=True)
        convertedFile = open(odtTempFileName, "rb")
        convertedContent = convertedFile.read()
        inputQueue.put((odtTempFileName, convertedContent))

    def listFiles(self):
        return self.fileList

    def getCount(self):
        return self.count

    def getCategories(self):
        return sorted(self.categoryDict.keys())

    def getCountInCategory(self, category):
        return self.categoryDict[category]["count"]

    def getExtensions(self):
        return sorted(self.extensionDict.keys())

    def getCountInExtension(self, extension):
        return self.extensionDict[extension]["count"]

    def getLanguages(self):
        return sorted(self.languageDict.keys())

    def getCountInLanguage(self, language):
        return self.languageDict[language]["count"]

    def getLanguageCount(self):
        resList = []
        for (lang, langDict) in self.languageDict.items():
            resList.append((lang, langDict["count"]))
        return sorted(resList, reverse=True, key=lambda tup: tup[1])

    def getExtensionCount(self):
        resList = []
        for (ext, extDict) in self.extensionDict.items():
            resList.append((ext, extDict["count"]))
        return sorted(resList, reverse=True, key=lambda tup: tup[1])


def parse_args(availableCommands):
    parser = argparse.ArgumentParser(description=__doc__)
    commandsHelp = "Available commands: %s" % (", ".join(availableCommands))
    parser.add_argument(metavar="CMD",
                        dest="command",
                        help=commandsHelp)
    parser.add_argument(metavar="ZIPFILE",
                        dest="files",
                        nargs="+",
                        help="Space separated list of zip files to handle")
    parser.add_argument("-r",
                        "--randomize",
                        dest="randomize",
                        action="store_true",
                        help="Randomize the processing order of zip files and responses")
    parser.add_argument("-c",
                        "--convert2odt",
                        dest="convert2odt",
                        action="store_true",
                        help="Converts almost all non-odt:s to the .odt format for further processing. This takes time.")
    parser.add_argument("--progress",
                        metavar="N",
                        dest="progress",
                        type=int,
                        default=0,
                        help="Show number of files processed (every N file)")
    parser.add_argument("--names",
                        dest="printNames",
                        action="store_true",
                        help="Print filenames of all processed files")
    parser.add_argument("-j",
                        dest="processes",
                        default=max(multiprocessing.cpu_count() - 1, 1),
                        type=int,
                        help="Number of processes to use. Defaults to number of CPUs - 1.")
    parser.add_argument("-n",
                        "--num",
                        dest="numberOfFiles",
                        type=int,
                        metavar="NUM",
                        default=0,
                        help="Abort after NUM files analyzed")
    parser.add_argument("-q",
                        "--queue-size",
                        dest="queueSize",
                        type=int,
                        default=10,
                        metavar="SIZE",
                        help="Size of the queue of files to analyze")
    parser.add_argument("--file-pattern",
                        dest="filePattern",
                        metavar="PATTERN",
                        default="*",
                        help="File pattern for files to analyze")
    parser.add_argument("--offset",
                        dest="offset",
                        metavar="NUM",
                        type=int,
                        help="Skip the first NUM files")
    parser.add_argument("--wipe-db",
                        dest="wipeDatabase",
                        action="store_true",
                        help="Wipe the SQLite file before saving analysis results")

    return parser.parse_args()

def typographicAnalyze(queue, zipFile, filename, convert2odt):
    fileending = filename.lower()[-5::]
    if fileending.endswith(".odt"):
        odtFilename = filename
        odtContent = zipFile.read(odtFilename)

        queue.put((odtFilename, odtContent))

    else:
        if not convert2odt:
            return
        if fileending.endswith(".doc"):
            self.convertFiles(tempdir, zipFile, filename, queue, ".doc")
        elif   fileending.endswith(".docx"):
            self.convertFiles(tempdir, zipFile, filename, queue, ".docx")
        elif fileending.endswith(".rtf"):
            self.convertFiles(tempdir, zipFile, filename, queue, ".rtf")
        elif fileending.endswith(".pdf"):
            self.convertFiles(tempdir, zipFile, filename, queue, ".pdf")
        else:
            return


def textBasedAnalyze(queue, zipFile, filename):
    content = zipFile.read(filename)
    queue.put((filename, content))


def main():
    """Main function for running the analyzer.
    Options will be parsed from the command line."""

    availableCommands = ["analyze", "analyze_text", "list-forms", "stats"]

    args = parse_args(availableCommands)

    if not args.command in availableCommands:
        parser.error("Unknown command: %s" % (args.command))
    print("The following zip files will be handled:")
    print("\n".join(map(lambda s: "* %s" % (s), args.files)))

    count = 0
    zipHandler = ConsultationZipHandler()
    for zipFile in args.files:
        zipHandler.addZip(zipFile)

    print("")
    if args.command == "list-forms":
        print("List of consultation forms:")
        for file in zipHandler.listFiles():
            try:
                print("* %s" % (file))
            except UnicodeEncodeError:
                print("ERROR: Encoding error")
    elif args.command == "stats":
        print("Categories:")
        categories = zipHandler.getCategories()
        for category in categories:
            print("  %-55s: %5d" % (category, zipHandler.getCountInCategory(category)))
        print("")
        print("File extensions:")
        for (ext, count) in zipHandler.getExtensionCount():
            print("  %-5s: %5d" % (ext, count))
        print("")
        print("Languages:")
        for (lang, count) in zipHandler.getLanguageCount():
            print("  %-2s: %5d" % (lang, count))
        print("")
        print("NUMBER OF FILES: %d" % (zipHandler.getCount()))
        print("")
        count += zipHandler.getCount()
    elif args.command == "analyze":
        zipHandler.analyze(lambda q, z, f: typographicAnalyze(q, z, f, args.convert2odt),
                           typographicAnalyzeWorker,
                           numProcesses=args.processes,
                           randomize=args.randomize,
                           showProgress=args.progress,
                           printNames=args.printNames,
                           numberOfFiles=args.numberOfFiles,
                           queueSize=args.queueSize,
                           filePattern=args.filePattern,
                           skip=args.offset,
                           convert2odt=args.convert2odt,
                           wipeDatabase=args.wipeDatabase)
    elif args.command == "analyze_text":
        zipHandler.analyze(textBasedAnalyze,
                           textBasedAnalyzeWorker,
                           numProcesses=args.processes,
                           randomize=args.randomize,
                           showProgress=args.progress,
                           printNames=args.printNames,
                           numberOfFiles=args.numberOfFiles,
                           queueSize=args.queueSize,
                           filePattern=args.filePattern,
                           skip=args.offset,
                           convert2odt=args.convert2odt,
                           wipeDatabase=args.wipeDatabase)

if __name__ == "__main__":
    multiprocessing.freeze_support() #Only for Windows executables (py2exe etc.)
    main()
