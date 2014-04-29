#!python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

from parsing_test_laban import getTextRecursive
import os, sys
import zipfile as zf
from xml.sax import parse, ContentHandler
import xml.dom.minidom
            
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
                    print( ans)
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
    
    #Listing the nodes and putting their names in a list.
    underlinelist = []
    for nod in underlinenodes:
        if nod.hasAttribute('style:name'):
            underlinelist.append(nod.getAttribute('style:name'))
    
    return underlinelist
    
def findAnswers(odtfile,questfile):
    """
    This function finds the answers in the odtfile by searching for each string
    in the questfile in succession through the text:p parts and returning the
    underlined answer between the question. If no underline is found
    NO RESPONSE is returned.
    """
    underlinedstyles = findStyles(odtfile)
    questlist = []
    with open(questfile,'r') as tmpfile:
        tmpstring = tmpfile.read()
        questlist = tmpstring.split('\n')[:-1] #The last element is empty and should be ignored.
    
#    print( len(questlist),"\n")
    zipodt = zf.ZipFile(odtfile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    
    paras = doc.getElementsByTagName('text:p')
    anslist = []
    # This part finds the first question and saves that place using the index i
    questcounter = 0 #Used to see if the paragraph matches one of the questions
    startindex = 0
    for i in range(len(paras)):
        paragraphtext = getTextRecursive(paras[i])
#        for ch in paras[i].childNodes:
#                if ch.nodeType == ch.TEXT_NODE:
#                    paragraphtext = paragraphtext + ch.data
#        print( paragraphtext)
#        print questlist[questcounter]
        if questlist[questcounter] in paragraphtext:
#            print( "Hello!")
            questcounter = questcounter + 1
            startindex = i
            break
#    print( startindex)
    foundans = False #A Boolean that indicates if a question has been answered
    # This part searches through the children until it finds an underlined part
    for i in range(startindex,len(paras)):
        paragraphtext = getTextRecursive(paras[i])
#        for ch in paras[i].childNodes:
#            if ch.nodeType == ch.TEXT_NODE:
#                paragraphtext = paragraphtext + ch.data
#        print( questlist[questcounter].encode('utf-8'))
#        print( paragraphtext.encode('utf-8'))
#        print( anslist)
        if questcounter >= len(questlist): pass
        elif questlist[questcounter] in paragraphtext:
#            print(paragraphtext)
#            print('')
            if not foundans: anslist.append('NO COMMENT') # If it got to the next question without finding an answer it adds NO COMMENT
            questcounter = questcounter + 1
            foundans = False
        if paras[i].hasAttribute('text:style-name'):
            if paras[i].getAttribute('text:style-name') in underlinedstyles: # It checks if the style is among the styles that underlines the text
                paragraphtext = ''
                for ch in paras[i].childNodes:
                    if ch.nodeType == ch.TEXT_NODE:
                        paragraphtext = paragraphtext + ch.data
                anslist.append(paragraphtext)
                foundans = True
    
    #The code doesn't find the last unaswered question. When we add the ability
    #to store [open question] this should be changed! For now, it just adds
    #a last unanswered tag for the last question.
    if len(anslist) == 79:
        anslist.append('NO COMMENT')
    return anslist
if __name__ == '__main__':
    """
    Change phrase to the search string and filename to the .odt file
    you want to search. It will find the paragraphs where phrase matches
    and print the paragraph
    """
    filename = 'input/TMP/a.-alcubilla_en.odt' #sys.argv[0] 
    phrase =  'Name:'#sys.argv[1]
    e = findAnswers(filename,'quest_stub')
    print( len(e))
    print('')
    for i in e:
        print(i)
    """
    if zipfile.is_zipfile(filename):
        myodf = OdfReader(filename) # Create object.
        myodf.showManifest()        # Tell me what files
                                    # we have here
        myodf.getContents()         # Get the raw
                                    # paragraph text.
        myodf.findIt(phrase)        # find the phrase ...
    """
