#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Parsing test by Laban
Find all text:list elements in an ODT file and print the text content
"""

# Note to self: Keep this script working with
# both "python" (2.7.x) and "python3"!

__author__ = "Henrik Laban Torstensson, Andreas Söderlund, Timmy Larsson"
__license__ = "MIT"


import re
import xml.dom.minidom

def getTextRecursive(element):
    text = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            text.append(node.data)
        else:
            text.append(getTextRecursive(node))

    joined = " ".join(text)
    return re.sub(" +", " ", joined).strip() # Remove duplicate, leading and trailing spaces


def main():
    filename = "input/users/a.-alcubilla_en/content.xml"

    f = open(filename)
    fileContent = f.read()
    f.close()

    dom = xml.dom.minidom.parseString(fileContent)

    textLists = dom.getElementsByTagName("text:list")
    print( len(textLists))
    print()
    for item in textLists:
        print( getTextRecursive(item))
        print()

if __name__ == "__main__":
    main()

