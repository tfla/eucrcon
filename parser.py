#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

import os
import sys
import zipfile as zf
import xml.dom.minidom

from parsing_test_laban import getTextRecursive
from xml.sax import parse, ContentHandler
            
def findName(odtFile, nameTag='Name:'):
    """
    Finds the name of the respondent by searching for the string
    nameTag and returning the string after that.
    """
    zipodt = zf.ZipFile(odtFile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    paras = doc.getElementsByTagName("text:p")

    ans = ""
    
    for st in paras:
        for txt in st.childNodes:
            if txt.nodeType == txt.TEXT_NODE:
                if nameTag in txt.data:
                    for cn in st.nextSibling.childNodes:
                        if cn.nodeType == cn.TEXT_NODE:
                            ans += cn.data + " "
                    #TODO: Remove print when done.
                    print(ans)
                    return ans
    return "Could not find the string {}".format(nameTag)

def findStyles(odtFile, styleTag='style:text-underline-type'):
    """
    This function will search through the file 'content.xml' to find
    the styles that underline the text in the file.
    """
    zipodt = zf.ZipFile(odtFile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    
    # Sees if there exists a child with tag office:automatic-styles
    tempList = doc.getElementsByTagName("office:automatic-styles")    
    if len(tempList) == 1:
        allStyles = tempList[0]
    elif len(tempList) > 1:
        return "Too many tags with name office:automatic-styles in content.xml!"
    else:
        return "No tag with name office:automatic-styles in content.xml!"
    
    #find those styles that are underlined
    underlineNodes = []
    for node in allStyles.childNodes:
        if node.hasChildNodes():
            for chlNode in node.getElementsByTagName('style:text-properties'):
                if chlNode.hasAttributes():
                    if chlNode.hasAttribute(styleTag):
                        underlineNodes.append(node)
    
    #Listing the nodes and putting their names in a list.
    underlineList = []
    for node in underlineNodes:
        if node.hasAttribute('style:name'):
            underlineList.append(node.getAttribute('style:name'))
    
    return underlineList
    
def findAnswers(odtFile, questFile):
    """
    This function finds the answers in the odtFile by searching for each string
    in the questFile in succession through the text:p parts and returning the
    underlined answer between the questions. If no underline is found,
    "NO RESPONSE" is returned.
    """
    underlinedStyles = findStyles(odtFile)
    questList = []
    with open(questFile, 'r') as tmpfile:
        tmpstring = tmpfile.read()
        questList = tmpstring.split('\n')[:-1] #The last element is empty and should be ignored.
    
#    print(len(questList), "\n")
    zipodt = zf.ZipFile(odtFile)
    cont = zipodt.read('content.xml')
    doc = xml.dom.minidom.parseString(cont)
    
    paras = doc.getElementsByTagName('text:p')
    ansList = []
    # This part finds the first question and saves that place using the index i
    questCounter = 0 #Used to see if the paragraph matches one of the questions
    startindex = 0
    for i in range(len(paras)):
        paragraphText = getTextRecursive(paras[i])
#        for ch in paras[i].childNodes:
#                if ch.nodeType == ch.TEXT_NODE:
#                    paragraphText += ch.data
#        print(paragraphText)
#        print(questList[questCounter])
        if questList[questCounter] in paragraphText:
#            print("Hello!")
            questCounter += 1
            startindex = i
            break
#    print(startindex)
    foundAns = False #A Boolean that indicates if a question has been answered
    # This part searches through the children until it finds an underlined part
    for i in range(startindex, len(paras)):
        paragraphText = getTextRecursive(paras[i])
#        for ch in paras[i].childNodes:
#            if ch.nodeType == ch.TEXT_NODE:
#                paragraphText += ch.data
#        print(questList[questCounter].encode('utf-8'))
#        print(paragraphText.encode('utf-8'))
#        print(ansList)
        if questCounter >= len(questList):
            pass
        elif questList[questCounter] in paragraphText:
#            print(paragraphText)
#            print('')
            if not foundAns:
                ansList.append('NO COMMENT') # If it got to the next question without finding an answer it adds NO COMMENT
            questCounter += 1
            foundAns = False
        if paras[i].hasAttribute('text:style-name'):
            if paras[i].getAttribute('text:style-name') in underlinedStyles: # It checks if the style is among the styles that underlines the text
                paragraphText = ''
                for ch in paras[i].childNodes:
                    if ch.nodeType == ch.TEXT_NODE:
                        paragraphText += ch.data
                ansList.append(paragraphText)
                foundAns = True
    
    #The code doesn't find the last unaswered question. When we add the ability
    #to store [open question] this should be changed! For now, it just adds
    #a last unanswered tag for the last question.
    if len(ansList) == 79:
        ansList.append('NO COMMENT')
    return ansList

if __name__ == '__main__':
    """
    Change phrase to the search string and filename to the .odt file
    you want to search. It will find the paragraphs where phrase matches
    and print the paragraph
    """
    filename = 'input/users/a.-alcubilla_en.odt' #sys.argv[0] 
    phrase =  'Name:' #sys.argv[1]
    e = findAnswers(filename, 'quest_stub')
    print(len(e))
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
