#!python
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
import os
import sys
import zipfile

if sys.version_info >= (3,):
    from io import StringIO
else:
    from cStringIO import StringIO

class ConsultationZip:
    """
    Class representing a zip file with consultation form responses
    """

    def __init__(self, filename):
        self.filename = filename
        self.zipFile = zipfile.ZipFile(self.filename)
        self.index()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def index(self):
        """Read statistics in zip file
        """

        self.categoryDict = {}
        self.extensionDict = {}

        # Loop through all files in the zip file
        # and count the number of files in different
        # categories and with different extensions
        for filename in self.zipFile.namelist():
            category = os.path.dirname(filename)
            formName = os.path.basename(filename)
            if formName == "":
                # Directory entry
                continue
            extension = formName.split(".")[-1]
            if category in self.categoryDict.keys():
                self.categoryDict[category]["count"] += 1
            else:
                extensionDict = {extension: {"count": 1}}
                self.categoryDict[category] = {"count": 1}
            if extension in self.extensionDict.keys():
                self.extensionDict[extension]["count"] += 1
            else:
                extensionDict = {extension: {"count": 1}}
                self.extensionDict[extension] = {"count": 1}


    def listFiles(self):
        return self.zipFile.namelist()

    def getCategories(self):
        return sorted(self.categoryDict.keys())

    def getCountInCategory(self, category):
        return self.categoryDict[category]["count"]

    def getExtensions(self):
        return sorted(self.extensionDict.keys())

    def getCountInExtension(self, extension):
        return self.extensionDict[extension]["count"]
        

def main():
    """Main function for running the analyzer.
    Options will be parsed from the command line."""

    availableCommands = ["analyze", "list-forms", "stats"]

    parser = argparse.ArgumentParser(description=__doc__)
    commandsHelp = "Available commands: %s" % (", ".join(availableCommands))
    parser.add_argument(metavar="CMD",
                        dest="command",
                        help=commandsHelp)
    parser.add_argument(metavar="ZIPFILE",
                        dest="files",
                        nargs="+",
                        help="Space separated list of zip files to handle")

    args = parser.parse_args()

    if not args.command in availableCommands:
        parser.error("Unknown command: %s" % (args.command))
    print("The following zip files will be handled:")
    print("\n".join(map(lambda s: "* %s" % (s), args.files)))

    print("")
    for file in args.files:
        print("Handling %s..." % (file))
        
        with ConsultationZip(file) as zip:
            if args.command == "list-forms":
                print("List of consultation forms:")
                print("\n".join(map(lambda s: "* %s" % (s), zip.listFiles())))
            elif args.command == "stats":
                print("Categories:")
                categories = zip.getCategories()
                for category in categories:
                    print("  %-55s: %5d" % (category, zip.getCountInCategory(category)))
                print("File extensions:")
                for extension in zip.getExtensions():
                    print("  %-6s: %5d" % (extension, zip.getCountInExtension(extension)))


if __name__ == "__main__":
    main()
