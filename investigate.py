#!python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

from parsing_test_laban import getTextRecursive
import os, sys
import zipfile as zf
from xml.sax import parse, ContentHandler
import xml.dom.minidom
from parser import *

def main():
    inp = sys.argv[1]
    ans = findAnswers(inp,'quest_stub')
    styles = findStyles(inp)
    print("investigating the file {}".format(inp))
    print("Number of answered questions: {}".format(len(ans)))
    print("Number of underlined styles: {}".format(len(styles)))
    for i in ans:
        print(i)
    
    
if __name__ == "__main__":
    main()