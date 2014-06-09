#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Main program for analyzing the downloaded files.
Python 3 is highly recommended since it handles
unicode better.
"""

# Note to self: Keep this script working with
# both "python" (2.7.x) and "python3"!

__author__ = "Henrik Laban Torstensson, Andreas Söderlund, Timmy Larsson"
__license__ = "MIT"

import argparse
import multiprocessing
import os
import parser
import random
import signal
import sys
import time
import zipfile

if sys.version_info >= (3,):
    from io import BytesIO as FileLike
else:
    from cStringIO import StringIO as FileLike


def processWorker(iq, oq):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Processes will receive SIGINT on Ctrl-C in main program. Just ignore it.
    resDict = {}
    for odtFilename, odtContent in iter(iq.get, "STOP"):
        odtFile = FileLike(odtContent) #FileLike provides seek()
        if zipfile.is_zipfile(odtFile):
            try:
                resDict = parser.parser(odtFile)
            except (parser.NumberingException, parser.NoAnswerException) as e:
                resDict["exceptionString"] = str(e)
                print("Error parsing {}: {}".format(odtFilename, str(e)))
        else:
            resDict["error"] = "Not a valid zip file"
            print("ERROR: {} is not a valid zip file!".format(odtFilename))
        odtFile.close()

        oq.put(resDict)


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
        self.zipFiles = {}      # filename -> ZipFile object

    def addZip(self, zipFilename):
        """
        Read statistics in zip file
        """

        zipFile = zipfile.ZipFile(zipFilename)
        self.zipFiles[zipFilename] = zipFile # Save in instance dict
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

    def analyze(self, randomize=False, showProgress=False, printNames=False, numProcesses=1, numberOfFiles=0, queueSize=100):
        numOfFilesToAnalyze = min(self.getCount(), numberOfFiles)
        zipFilenames = self.zipFiles.keys()
        if randomize:
            random.shuffle(zipFilenames)
        count = 0
        print("Queue size:", queueSize)
        print("Analyzing using {} process(s)...".format(numProcesses))
        inputQueue = multiprocessing.Queue(queueSize)
        resultQueue = multiprocessing.Queue()
        processes = []
        for i in range(numProcesses):
            process = multiprocessing.Process(name="{}".format(i + 1), target=processWorker, args=[inputQueue, resultQueue])
            process.start()
            processes.append(process)
        startTime = time.time()
        abort = False
        try:
            for zipFilename in zipFilenames:
                if abort:
                    break
                zipFile = self.zipFiles[zipFilename] #ZipFile object
                filenames = self.fileListByZip[zipFilename]
                if randomize:
                    random.shuffle(filenames)
                for filename in filenames:
                    if numberOfFiles:
                        if count >= numberOfFiles:
                            print("Aborting after enqueuing {} files".format(numberOfFiles))
                            abort = True
                            break
                    if not filename.lower().endswith(".odt"):
                        continue
                    if printNames:
                        print("Enqueuing {}...".format(filename))
                    odtFilename = filename
                    odtContent = zipFile.read(odtFilename)

                    inputQueue.put((odtFilename, odtContent))

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
        for i in range(numOfFilesToAnalyze): # There must be exactly this number of dictionaries in the result queue
            results.append(resultQueue.get())
        for process in processes:
            process.join()
        print("{:.2%} analyzed ({}/{})".format(float(count) / float(numOfFilesToAnalyze), count, numOfFilesToAnalyze))
        duration = time.time() - startTime
        if count > 0:
            print("{} files analyzed in {:.1f} s (avg {:.3f} s)".format(count, duration, duration/count))

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

    return parser.parse_args()


def main():
    """Main function for running the analyzer.
    Options will be parsed from the command line."""

    availableCommands = ["analyze", "list-forms", "stats"]

    args = parse_args(availableCommands)

    if not args.command in availableCommands:
        parser.error("Unknown command: %s" % (args.command))
    print("The following zip files will be handled:")
    print("\n".join(map(lambda s: "* %s" % (s), args.files)))

    print("")
    count = 0
    zipHandler = ConsultationZipHandler()
    for zipFile in args.files:
        print("Adding %s to handling list..." % (zipFile))
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
        zipHandler.analyze(numProcesses=args.processes,
                           randomize=args.randomize,
                           showProgress=args.progress,
                           printNames=args.printNames,
                           numberOfFiles=args.numberOfFiles,
                           queueSize=args.queueSize)

if __name__ == "__main__":
    multiprocessing.freeze_support() #Only for Windows executables (py2exe etc.)
    main()
