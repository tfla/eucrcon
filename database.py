#!/usr/bin/env python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Handles the database
"""

# Note to self: Keep this script working with
# both "python" (2.7.x) and "python3"!

__author__ = "Henrik Laban Torstensson, Andreas Söderlund, Timmy Larsson"
__license__ = "MIT"

import sqlite3

class Database():
    """Represents a SQLite database"""

    def __init__(self, database='responses.sqlite'):
        """Initialize a connection to the database <database> and
        create tables needed if they don't exist."""

        conn = sqlite3.connect(database)
        self.cur = conn.cursor()

        self.cur.execute('''SELECT name FROM sqlite_master WHERE type='table' ORDER BY name''')
        ans = self.cur.fetchall()

        if not ('answers',) in ans:
            print("Creating table 'answers'...")
            self.cur.execute('''CREATE TABLE answers (id INTEGER PRIMARY KEY AUTOINCREMENT, num INTEGER, question INTEGER, choice TEXT, freeText TEXT)''')
        if not ('forms',) in ans:
            print("Creating table 'forms'...")
            self.cur.execute('''CREATE TABLE forms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, lang TEXT)''')
        if not ('questions',) in ans:
            print("Creating table 'questions'...")
            self.cur.execute('''CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, type TEXT)''')

    def putQuestion(self, question, _type):
        for tmp in [(question, _type)]:
            self.cur.execute('INSERT INTO questions VALUES (NULL, ?, ?)', tmp)
        
    def listQuestions(self):
        questions = self.cur.execute('SELECT * FROM questions ORDER BY id')
        return questions.fetchall()
        
    def getQuestion(self, _id):
        question = self.cur.execute('SELECT * FROM questions WHERE id=?', _id)
        return question.fetchall()
        
    def getQuestionsByType(self, _type):
        questions = self.cur.execute('SELECT * FROM questions WHERE type=?', _type)
        return questions.fetchall()
        
    def putAnswer(self, num, question, choice, freeText):
        for tmp in [(num, question, choice, freeText)]:
            self.cur.execute('INSERT INTO questions VALUES (NULL, ?, ?, ?, ?)', tmp)

    def listAnswers(self):
        answers = self.cur.execute('SELECT * FROM answers ORDER BY id')
        return answers.fetchall()
    
    def getAnswer(self, _id):
        answer = self.cur.execute('SELECT * FROM answers WHERE id=?', _id)
        return answer.fetchall()
        
    def getAnswerByNum(self, num):
        answer = self.cur.execute('SELECT * FROM answers WHERE num=?', num)
        return answer.fetchall()
        
    def getAnswerByQuestion(self, question):
        answer = self.cur.execute('SELECT * FROM answers WHERE question=?', question)
        return answer.fetchall()
        
    def getAnswerByChoice(self, choice):
        answer = self.cur.execute('SELECT * FROM answers WHERE choice=?', choice)
        return answer.fetchall()
        
    def putForm(self, name, _type, lang):
        for tmp in [(name, _type, lang)]:
            self.cur.execute('INSERT INTO questions VALUES (NULL, ?, ?, ?)', tmp)
        
    def listForms(self):
        forms = self.cur.execute('SELECT * FROM forms ORDER BY id')
        return forms.fetchall()

    def getForm(self, _id):
        form = self.cur.execute('SELECT * FROM forms WHERE id=?', _id)
        return form.fetchall()
        
    def getFormByName(self, name):
        form = self.cur.execute('SELECT * FROM forms WHERE name=?', name)
        return form.fetchall()
        
    def getFormByType(self, _type):
        forms = self.cur.execute('SELECT * FROM forms WHERE type=?', _type)
        return forms.fetchall()

    def getFormByLang(self, lang):
        forms = self.cut.execute('SELECT * FROM forms WHERE lang=?', lang)
        return forms.fetchall()
        
    def save(self):
        self.cur.commit()


def test():
    """Tests the database handling by creating the database file
    with the defined schema"""

    db = Database()

if __name__ == "__main__":
    test()

