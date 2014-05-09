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

c = None

class Database():
    def __init__(self, database='responses.sqlite'):
        global c
        conn = sqlite3.connect(database)
        c = conn.cursor()

        c.execute('''SELECT name FROM sqlite_master WHERE type='table' ORDER BY name''')
        ans = c.fetchall()
        if (ans == [('answers',), ('forms',), ('questions',)]):
            pass
        if (ans == [('answers',), ('forms',)]):
            c.execute('''CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, type TEXT)''')
        if (ans == [('answers',), ('questions',)]):
            c.execute('''CREATE TABLE forms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT)''')
        if (ans == [('forms',), ('questions',)]):
            c.execute('''CREATE TABLE answers (id INTEGER PRIMARY KEY AUTOINCREMENT, num INTEGER, question INTEGER, choice TEXT, freeText TEXT)''')
        if (ans == [('answers',)]):
            c.execute('''CREATE TABLE forms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT)''')
            c.execute('''CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, type TEXT)''')
        if (ans == [('forms',)]):
            c.execute('''CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, type TEXT)''')
            c.execute('''CREATE TABLE answers (id INTEGER PRIMARY KEY AUTOINCREMENT, num INTEGER, question INTEGER, choice TEXT, freeText TEXT)''')
        if (ans == [('questions',)]):
            c.execute('''CREATE TABLE forms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT)''')
            c.execute('''CREATE TABLE answers (id INTEGER PRIMARY KEY AUTOINCREMENT, num INTEGER, question INTEGER, choice TEXT, freeText TEXT)''')
        if (ans == []):
            c.execute('''CREATE TABLE forms (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT)''')
            c.execute('''CREATE TABLE questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, type TEXT)''')
            c.execute('''CREATE TABLE answers (id INTEGER PRIMARY KEY AUTOINCREMENT, num INTEGER, question INTEGER, choice TEXT, freeText TEXT)''')

    def putQuestion(self, question, _type):
        for tmp in [(question, _type)]:
            c.execute('INSERT INTO questions VALUES (NULL, ?, ?)', tmp)
        
    def listQuestions(self):
        questions = c.execute('SELECT * FROM questions ORDER BY id')
        return questions.fetchall()
        
    def getQuestion(self, _id):
        question = c.execute('SELECT * FROM questions WHERE id=?', _id)
        return question.fetchall()
        
    def getQuestionsByType(self, _type):
        questions = c.execute('SELECT * FROM questions WHERE type=?', _type)
        return questions.fetchall()
        
    def putAnswer(self, num, question, choice, freeText):
        for tmp in [(num, question, choice, freeText)]:
            c.execute('INSERT INTO questions VALUES (NULL, ?, ?)', tmp)

    def listAnswers(self):
        answers = c.execute('SELECT * FROM answers ORDER BY id')
        return answers.fetchall()
    
    def getAnswer(self, _id):
        answer = c.execute('SELECT * FROM answers WHERE id=?', _id)
        return answer.fetchall()
        
    def getAnswerByNum(self, num):
        answer = c.execute('SELECT * FROM answers WHERE num=?', num)
        return answer.fetchall()
        
    def getAnswerByQuestion(self, question):
        answer = c.execute('SELECT * FROM answers WHERE question=?', question)
        return answer.fetchall()
        
    def getAnswerByChoice(self, choice):
        answer = c.execute('SELECT * FROM answers WHERE choice=?', choice)
        return answer.fetchall()
        
    def putForm(self, name, _type):
        for tmp in [(name, _type)]:
            c.execute('INSERT INTO questions VALUES (NULL, ?, ?)', tmp)
        
    def listForms(self):
        forms = c.execute('SELECT * FROM forms ORDER BY id')
        return forms.fetchall()

    def getForm(self, _id):
        form = c.execute('SELECT * FROM forms WHERE id=?', _id)
        return form.fetchall()
        
    def getFormByName(self, name):
        form = c.execute('SELECT * FROM forms WHERE name=?', name)
        return form.fetchall()
        
    def getFormByType(self, _type):
        forms = c.execute('SELECT * FROM forms WHERE type=?', _type)
        return forms.fetchall()
        
    def save(self):
        c.commit()
