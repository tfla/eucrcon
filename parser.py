#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

import os
import re
import sys
import zipfile as zf
from xml.dom import minidom

from xml.sax import parse, ContentHandler

def findAttributeRecursive(element, tagName):
    """
    Searches an element recursively to find if a certain attribute is
    present.
    """
    boo = False
    if element.hasAttribute(tagName):
        boo = True
    for node in element.childNodes:
        if isinstance(node, minidom.Element) and node.hasAttributes():
            if node.hasAttribute(tagName):
                boo = True
            else:
                boo = findAttributeRecursive(node, tagName)
        if boo: break
    else:
        if element.hasAttribute(tagName):
            boo = True
    return boo
       
def getTextRecursive(element):
    """
    Return all text in an element (everything which is not within tags).
    Duplicate, leading and trailing spaces are removed.
    """

    text = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            text.append(node.data)
        else:
            text.append(getTextRecursive(node))

    joined = " ".join(text)
    return re.sub(" +", " ", joined).strip() # Remove duplicate, leading and trailing spaces

def findUnderlinedRecursive(element, styles ,tag = 'text:style-name'):
    """
    This function searches through the element recursively to see if there exists
    a tag with a value that exists in the list styles. If so, it returns True
    and the text which has this attribute (in this case, the underlined text)
    """
    if element.nodeName == 'text:p':
        paras = [element]
    else:
        paras = element.getElementsByTagName('text:p')
    text = [] # This will collect all the text that is (in this case) underlined
    for st in paras:
        if st.hasAttribute(tag):
            if st.getAttribute(tag) in styles: # It checks if the style is among the styles that underlines the text      
                paragraphText = ''
                for ch in st.childNodes:
                    if ch.nodeType == ch.TEXT_NODE:
                        paragraphText += ch.data
                text.append(paragraphText)
    if len(text) == 0: # If it didn't find any underlined text then len(text)==0 and False is returned
        return (False,' ')
    else:
        joined = " ".join(text)
        return (True,re.sub(" +", " ", joined).strip()) # Remove duplicate, leading and trailing spaces
                
def findName(element, nameTag='Name:'):
    """
    Finds the name of the respondent by searching for the string
    nameTag and returning the string after that.
    """
    
    paras = element.getElementsByTagName("text:p")

    ans = ""
    
    for st in paras:
        for txt in st.childNodes:
            if txt.nodeType == txt.TEXT_NODE:
                if nameTag in txt.data:
                    for cn in st.nextSibling.childNodes:
                        if cn.nodeType == cn.TEXT_NODE:
                            ans += cn.data + " "
                    return ans
    return "Could not find the string {}".format(nameTag)

def findStyles(element, styleTag='style:text-underline-type'):
    """
    This function will search through the file 'content.xml' to find
    the styles that underline the text in the file.
    """
    
    # Sees if there exists a child with tag office:automatic-styles
    tempList = element.getElementsByTagName("office:automatic-styles")    
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

def countTag(element, tag = 'text:continue-numbering'):
    
    paras = element.getElementsByTagName('office:body')[0].childNodes[0].childNodes
    
    counter = 0    
    for element in paras:
        if findAttributeRecursive(element, tag):
            counter = counter + 1
    return counter
    
    
def findAnswers(element, questions, openquest, styleTag='style:text-underline-type', tag = 'text:continue-numbering'):
    """
    This is the new updated findAnswers method, the old one is saved as findAnswers2.
    this function will go through all the childNodes of the node 'office:body'
    of the file content.xml. for each childNode it will see if there 'tag' is in
    the node recursively. If there is it will increase questionNr by one. if questionNr
    matches any of the numbers in 'questions' it will start seaching for an underlined
    text. If it finds underlined text the underlined text will be regarded as an
    answer and appended to the list 'ansList' if the function fins a new question
    without having found an underlined text it will append 'NO COMMENT' to the
    answer list. It will return a list containing the answers and possible free text.
    As it is now, free text is not implemented yet but is just added as ' ' for
    later compatibility.
    """
    underlinedStyles = findStyles(element, styleTag)
    
    paras = element.getElementsByTagName('office:body')[0].childNodes[0].childNodes # Open all the childNodes of 'office:body'
    numberOfCountAttribute = countTag(element, tag)
    if not numberOfCountAttribute == 100: # If there are more or less 'text:continue-numbering' than 100 then this function will fail!
        print("Found {} number of text:continue-numbering which is not supported".format(numberOfCountAttribute))
    
    ansList = [] # The answers.
    questionNr = 0 # will range from 0 to 99 as each element of paras is gone through
    foundQuest = False # If questionNr is in questions it turns to true
    for element in paras:
        if findAttributeRecursive(element, tag):
            if questionNr in questions:
                if foundQuest:
                    ansList.append(['NO COMMENT', ' ']) #If nothing has been underlined then no free text should exist.
                foundQuest = True
                if questionNr in openquest:
                    ansList.append(['OPEN QUESTION', ' ']) #implement a method to find the text added by the respondent!
                    foundQuest = False # If it's an open question then it has found an answer.
            questionNr = questionNr + 1
        if foundQuest:
            ifFound, text = findUnderlinedRecursive(element, underlinedStyles)
            if ifFound:
                ansList.append([text, ' ']) # Add a method to find the text added by the respondent!
                foundQuest = False # It has found an answer and start seaching for a new question.
    if len(ansList)<80: # The last [open question] is not found in this function and thus the last NO COMMENT is added manually.
        ansList.append(['OPEN QUESTION', ' ']) #implement a method to find the text added by the respondent!
    return ansList
                
    
def findAnswers2(odtFile, questFile):
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
    doc = minidom.parseString(cont)
    
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


def parseOdfFile(filename):
    """Parse an ODT file"""

    """
    Change phrase to the search string you want to search for.
    It will find the paragraphs where phrase matches
    and print the paragraph
    """
    phrase =  'Name:' #sys.argv[1]
    nam,typ,ans = parser(filename)
    print(len(ans))
    print('')
    for i in ans:
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
    return False

def parser(filename, questions=False, openquest=False, nameTag='Name:', styleTag='style:text-underline-type', numberingTag='text:continue-numbering'):
    """
    This is the main function that will open an .odt file and find the name of 
    the respondent and the answers to the 80 questions.
    nameTag is used to find the name of the respondent and will return the text
    following the string in nameTag.
    styleTag is used to find the answers. the text following the questions that
    matches the styles containing styleTag will be regarded as answers.
    numberingTag will be used to find the questions. Each time numberingTag is 
    found it has the possibility of being a question as defined by the questions
    list.
    Returns the name of the respondent, the type of respondent (not implemented yet)
    and the answers.
    """
    
    # There are a total of 100 places in the file (hopefully) that have the part
    # 'text:continue-numbering'. All of the questions will have these before.
    # The list 'questions' will mark at wich number among the tags that each question
    # appears.
    if not questions:
        questions = list(range(14,34)) + list(range(35,78)) + list(range(79,87)) + [88, 89, 90, 92, 93, 94, 96, 97, 99]
        
    # This is not used at the moment, but this is a list of where all the [open question]'s
    # appears.
    if not openquest:
        openquest = [16,17,27,29,30,31,32,37,39,41]+list(range(43,50))+[51,52,53,57,58,59,60,62,63,65,66,68,69,70,71,75,76,77,81,84,85,86,88,90,93,97,99]
    
    
    zipodt = zf.ZipFile(filename)
    cont = zipodt.read('content.xml')
    doc = minidom.parseString(cont)
    
    respondNam = findName(doc, nameTag)
    
    respondTyp = False # The type of the respondent (user/copyright holder/etc.). Not implemented yet!
    respondAns = findAnswers(doc, questions, openquest, styleTag, numberingTag)
    
    return respondNam, respondTyp, respondAns
    
if __name__ == '__main__':
    filename = sys.argv[1]
#    filename = 'input/users/a.-alcubilla_en.odt' #sys.argv[0]
#    if not os.path.isfile(filename):
#        print("ERROR: File {} not found. Make sure that input/users_en.zip is unzipped.".format(filename))
#        sys.exit(1)
#    parseOdfFile(filename)
    print(filename)
    respondNam, respondTyp, respondAns = parser(filename)
    print(respondNam)
    print( )
    for i in range(len(respondAns)):
        print('Question {}: {}').format(i+1, respondAns[i])
    print("Number of found answers: {}").format(len(respondAns))
    