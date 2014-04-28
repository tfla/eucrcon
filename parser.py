#
# This program will list out the uniq tag
# names in a XML document.
# Author: Kamran Husain
#

import os, sys
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
        for s in range(len(self.text_in_paras)):
#            print s.encode('utf-8')
            if name in self.text_in_paras[s]:
               print self.text_in_paras[s].encode('utf-8') 
            
def findName(odtfile, nametag='Name:'):
    """
    Finds the name of the respondent by searching for the string
    nametag and returning the string after that.
    """
    zipodt = zf.ZipFile(odtfile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    paras = doc.getElementsByTagName("text:p")

    ans = ""
    
    for st in paras:
        for txt in st.childNodes:
            if txt.nodeType == txt.TEXT_NODE:
                if nametag in txt.data:
                    for cn in st.nextSibling.childNodes:
                        if cn.nodeType == cn.TEXT_NODE:
                            ans = ans + cn.data + " "
                    #Remove print when done.
                    print ans
                    return ans
    return "Counld not find the string {}".format(nametag)

def findStyles(odtfile, styletag = 'style:text-underline-type'):
    """
    This function will search through the file 'content.xml' to find
    the styles that underline the text in the file.
    """
    zipodt = zf.ZipFile(odtfile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    
    # Sees if there exist a child with tag office:automatic-styles
    templist = doc.getElementsByTagName("office:automatic-styles")    
    if len( templist ) == 1:
        allstyles = templist[0]
    elif len( templist ) > 1:
        return "Too many tags with name office:automatic-styles in content.xml!"
    else: return "No tag with name office:automatic-styles in content.xml!"
    
    #find those styles that are underlined
    underlinenodes = []
    for nod in allstyles.childNodes:
        if nod.hasChildNodes():
            for chlnod in nod.getElementsByTagName('style:text-properties'):
                if chlnod.hasAttributes():
                    if chlnod.hasAttribute(styletag):
                        underlinenodes.append(nod)
    
    #printing the names of the styles for checking. Remove this later
    for nod in underlinenodes:
        if nod.hasAttribute('style:name'):
            print nod.getAttribute('style:name')
    
    return underlinenodes
    

if __name__ == '__main__':
    """
    Change phrase to the search string and filename to the .odt file
    you want to search. It will find the paragraphs where phrase matches
    and print the paragraph
    """
    filename = 'input/TMP/a.-alcubilla_en.odt' #sys.argv[0] 
    phrase =  'Name:'#sys.argv[1]
    e = findName(filename)
    """
    if zipfile.is_zipfile(filename):
        myodf = OdfReader(filename) # Create object.
        myodf.showManifest()        # Tell me what files
                                    # we have here
        myodf.getContents()         # Get the raw
                                    # paragraph text.
        myodf.findIt(phrase)        # find the phrase ...
    """