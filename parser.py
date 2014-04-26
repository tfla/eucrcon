#
# This program will list out the uniq tag
# names in a XML document.
# Author: Kamran Husain
#

import sys
import zipfile as zf
from xml.sax import parse, ContentHandler

class tagHandler(ContentHandler):
    def __init__(self, tagName = None):
        self.tag = tagName
        self.uniq = {}

    def startElement(self,name,attr):
        if self.tag == None:
            self.uniq[name] = 1;
        elif self.tag == name:
            self.uniq[name] = name
        # ignore attributes for now

    def getNames(self):
        return self.uniq.keys()
"""
if __name__ == '__main__':
    test = zf.ZipFile('a.-alcubilla_en.odt')
    ary = test.read('content.xml')
    myTagHandler = tagHandler()
    parse(ary, myTagHandler)
    myNames = [str(x) for x in myTagHandler.getNames()]
    myNames.sort()
    for x in myNames: print x
"""

import os, sys
import zipfile
import xml.dom.minidom

class OdfReader:
    def __init__(self,filename):
        """
        Open an ODF file.
        """
        self.filename = filename
        self.m_odf = zipfile.ZipFile(filename)
        self.filelist = self.m_odf.infolist()

    def showManifest(self):
        """
        Just tell me what files exist in the ODF file.
        """
        for s in self.filelist:
            #print s.orig_filename, s.date_time,
            s.filename, s.file_size, s.compress_size
            print s.orig_filename

    def getContents(self):
        """
        Just read the paragraphs from an XML file.
        """
        ostr = self.m_odf.read('content.xml')
        doc = xml.dom.minidom.parseString(ostr)
        paras = doc.getElementsByTagName('text:p')
        print "I have ", len(paras), " paragraphs "
        self.text_in_paras = []
        for p in paras:
            for ch in p.childNodes:
                if ch.nodeType == ch.TEXT_NODE:
                    self.text_in_paras.append(ch.data)

    def findIt(self,name):
        for s in self.text_in_paras:
            print s.encode('utf-8')
            if name in s:
               print s.encode('utf-8')


if __name__ == '__main__':
    """
    Change phrase to the search string and filename to the .odt file
    you want to search. It will find the paragraphs where phrase matches
    and print the paragraph
    """
    filename = 'a.-alcubilla_en.odt' #sys.argv[0] 
    phrase =  'In particular'#sys.argv[1]
    if zipfile.is_zipfile(filename):
        myodf = OdfReader(filename) # Create object.
        myodf.showManifest()        # Tell me what files
                                    # we have here
        myodf.getContents()         # Get the raw
                                    # paragraph text.
        myodf.findIt(phrase)        # find the phrase ...