#!python

class Form:
    """Holds interesting data from one response file (odt)
    """ 

    name = ""
    type = ""
    questions = []

    def __init__(self):
        pass    


class FormQuestion:
    """Holds data for the response to a single question in a form
    """ 

    number = 0 
    # The number of the question in the form (1 - ~80)

    choices = []
    # List of strings with the available choices if any 
    # (empty if "open question" or similar)

    markedChoice = None
    # String with the marked choice, or None if no choice
    # is marked or if several choices are marked

    freeText = ""
    # The respondent's free text answer to this question

