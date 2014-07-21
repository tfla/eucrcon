#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

#import os
import re
import sys
import zipfile as zf
from xml.dom import minidom

class NumberingException(Exception):
    pass
class NoAnswerException(Exception):
    pass

def hasAttributeRecursive(element, tagName):
    """
    Searches an element recursively to find if a certain attribute is
    present.
    """
    found = False
    for node in element.childNodes:
        if isinstance(node, minidom.Element) and node.hasAttributes():
            if node.hasAttribute(tagName):
                found = True
            else:
                found = hasAttributeRecursive(node, tagName)
        if found:
            break
    else:
        if element.hasAttribute(tagName):
            found = True
    return found
       
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
                        if cn.nodeType == cn.TEXT_NODE and not "…" in cn.data:
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
        if hasAttributeRecursive(element, tag):
            counter = counter + 1
    return counter
    
    
def findAnswers(element, questions, openquest, styleTags=['style:text-underline-type'], tag = 'text:continue-numbering'):
    """
    This is the new updated findAnswers method, the old one is saved as findAnswers2.
    this function will go through all the childNodes of the node 'office:body'
    of the file content.xml. for each childNode it will see if there 'tag' is in
    the node recursively. If there is it will increase questionNr by one. if questionNr
    matches any of the numbers in 'questions' it will start searching for an underlined
    text. If it finds underlined text the underlined text will be regarded as an
    answer and appended to the list 'ansList' if the function finds a new question
    without having found an underlined text it will append 'NO COMMENT' to the
    answer list. It will return a list containing the answers and possible free text.
    As it is now, free text is not implemented yet but is just added as ' ' for
    later compatibility.
    """
    
    underlinedStyles = findStyles(element, styleTags[0])
    for styleString in styleTags[1:]:
        tmpStyles = findStyles(element, styleString)
        if len(tmpStyles)>len(underlinedStyles):
            underlinedStyles = tmpStyles[:]
    
    paras = element.getElementsByTagName('office:body')[0].childNodes[0].childNodes # Open all the childNodes of 'office:body'
    numberOfCountAttribute = countTag(element, tag)
    if not numberOfCountAttribute == 100: # If there are more or less 'text:continue-numbering' than 100 then this function will fail!
        raise NumberingException("Found {} number of text:continue-numbering which is not supported".format(numberOfCountAttribute))
    
    ansList = [] # The answers.
    questionNr = 0 # will range from 0 to 99 as each element of paras is gone through
    foundQuest = False # If questionNr is in questions it turns to true
    for element in paras:
        if hasAttributeRecursive(element, tag):
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
                

def parser(filename, questions=None, openquest=None, nameTag='Name:', styleTags=['style:text-underline-type','style:text-underline-style'], numberingTag='text:continue-numbering'):
    """
    This is the main function that will open an .odt file and find the name of 
    the respondent and the answers to the 80 questions.
    nameTag is used to find the name of the respondent and will return the text
    following the string in nameTag.
    styleTags is used to find the answers. the text following the questions that
    matches the styles containing styleTags will be regarded as answers. The
    function will go through all the strings in the list styleTags and use the
    string that find the most styles as the one to find the relevant styles.
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
    respondAns = findAnswers(doc, questions, openquest, styleTags, numberingTag)
    # Converting every answer to YES/NO...
    for element in respondAns:
        if 'YES' in element[0]:
            element[0] = 'YES'
        if 'NO' in element[0]:
            if 'NO OPINION' in element[0]:
                element[0] = 'NO OPINION'
            if 'NOOPINION' in element[0]:
                element[0] = 'NO OPINION'
            if 'NO COMMENT' in element[0]:
                element[0] = 'NO COMMENT'
            else:
                element[0] = 'NO'
        
    # Checking if any answers were found
    tmpBool = False
    for element in respondAns:
        if element[0] not in ['NO COMMENT', 'OPEN QUESTION']: tmpBool = True
    if not tmpBool: 
        raise NoAnswerException("Didn't find any underlined answers in the file")
    ansDict = {'name': respondNam, 'type': respondTyp, 'answers': respondAns}
    return ansDict
    
if __name__ == '__main__':
    filename = sys.argv[1]
#    filename = 'input/users/a.-alcubilla_en.odt' #sys.argv[0]
#    if not os.path.isfile(filename):
#        print("ERROR: File {} not found. Make sure that input/users_en.zip is unzipped.".format(filename))
#        sys.exit(1)
#    parseOdfFile(filename)
    print(filename)
    ansDict = parser(filename)
    respondNam = ansDict['name']
    respondAns = ansDict['answers']
    print(respondNam)
    print( )
    for i in range(len(respondAns)):
        print('Question {}: {}'.format(i+1, respondAns[i]))
    print("Number of found answers: {}".format(len(respondAns)))
    
