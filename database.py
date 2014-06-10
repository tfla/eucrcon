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

        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()

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
            self.putQuestion("[In particular if you are an end user/consumer:] Have you faced problems when trying to access services in an EU Member State other than the one in which you live?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are a service provider:] Have you faced problems when seeking to provide online services across borders in the EU?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are a right holder or a collective management organisation:] How often are you asked to grant multi-territorial licences? Please indicate, if possible, the number of requests per year and provide examples indicating the Member State, the sector and the type of content concerned.", "OPEN")
            self.putQuestion("If you have identified problems in the answers to any of the questions above – what would be the best way to tackle them?", "OPEN")
            self.putQuestion("[In particular if you are a right holder or a collective management organisation:] Are there reasons why, even in cases where you hold all the necessary rights for all the territories in question, you would still find it necessary or justified to impose territorial restrictions on a service provider (in order, for instance, to ensure that access to certain content is not possible in certain European countries)?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are e.g. a broadcaster or a service provider:] Are there reasons why, even in cases where you have acquired all the necessary rights for all the territories in question, you would still find it necessary or justified to impose territorial restrictions on the service recipient (in order for instance, to redirect the consumer to a different website than the one he is trying to access)?", "YES/NO/NO OPINION")
            self.putQuestion("Do you think that further measures (legislative or non-legislative, including market-led solutions) are needed at EU level to increase the cross-border availability of content services in the Single Market, while ensuring an adequate level of protection for right holders?", "YES/NO/NO OPINION")
            self.putQuestion("Is the scope of the “making available” right in cross-border situations – i.e. when content is disseminated across borders – sufficiently clear?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are a right holder:] Could a clarification of the territorial scope of the “making available” right have an effect on the recognition of your rights (e.g. whether you are considered to be an author or not, whether you are considered to have transferred your rights or not), on your remuneration, or on the enforcement of rights (including the availability of injunctive relief1)?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you a service provider or a right holder:] Does the application of two rights to a single act of economic exploitation in the online environment (e.g. a download) create problems for you?", "YES/NO/NO OPINION")
            self.putQuestion("Should the provision of a hyperlink leading to a work or other subject matter protected under copyright, either in general or under specific circumstances, be subject to the authorisation of the rightholder?", "YES/NO/NO OPINION")
            self.putQuestion("Should the viewing of a web-page where this implies the temporary reproduction of a work or other subject matter protected under copyright on the screen and in the cache memory of the user’s computer, either in general or under specific circumstances, be subject to the authorisation of the rightholder?", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are an end user/consumer:] Have you faced restrictions when trying to resell digital files that you have purchased (e.g. mp3 file, e-book)? ", "YES/NO/NO OPINION")
            self.putQuestion("[In particular if you are a right holder or a service provider:] What would be the consequences of providing a legal framework enabling the resale of previously purchased digital content? Please specify per market (type of content) concerned.", "OPEN")
            self.putQuestion("Would the creation of a registration system at EU level help in the identification and licensing of works and other subject matter?", "YES/NO/NO OPINION")
            self.putQuestion("What would be the possible advantages of such a system? ", "OPEN")
            self.putQuestion("What would be the possible disadvantages of such a system? ", "OPEN")
            self.putQuestion("What incentives for registration by rightholders could be envisaged?", "OPEN")
            self.putQuestion("What should be the role of the EU in promoting the adoption of identifiers in the content sector, and in promoting the development and interoperability of rights ownership and permissions databases?", "OPEN")
            self.putQuestion("Are the current terms of copyright protection still appropriate in the digital environment?", "YES/NO/NO OPINION")
            self.putQuestion("Are there problems arising from the fact that most limitations and exceptions provided in the EU copyright directives are optional for the Member States?", "YES/NO/NO OPINION")
            self.putQuestion("Should some/all of the exceptions be made mandatory and, if so, is there a need for a higher level of harmonisation of such exceptions?", "YES/NO/NO OPINION")
            self.putQuestion("Should any new limitations and exceptions be added to or removed from the existing catalogue? Please explain by referring to specific cases.", "OPEN")
            self.putQuestion("Independently from the questions above, is there a need to provide for a greater degree of flexibility in the EU regulatory framework for limitations and exceptions?", "YES/NO/NO OPINION")
            self.putQuestion("If yes, what would be the best approach to provide for flexibility? (e.g. interpretation by national courts and the ECJ, periodic revisions of the directives, interpretations by the Commission, built-in flexibility, e.g. in the form of a fair-use or fair dealing provision / open norm, etc.)? Please explain indicating what would be the relative advantages and disadvantages of such an approach as well as its possible effects on the functioning of the Internal Market.", "OPEN")
            self.putQuestion("Does the territoriality of limitations and exceptions, in your experience, constitute a problem?", "YES/NO/NO OPINION")
            self.putQuestion("In the event that limitations and exceptions established at national level were to have cross-border effect, how should the question of “fair compensation” be addressed, when such compensation is part of the exception? (e.g. who pays whom, where?)", "OPEN")
            self.putQuestion("(a) [In particular if you are an institutional user:] Have you experienced specific problems when trying to use an exception to preserve and archive specific works or other subject matter in your collection? (b) [In particular if you are a right holder:] Have you experienced problems with the use by libraries, educational establishments, museum or archives of the preservation exception?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved?", "OPEN")
            self.putQuestion("If your view is that a legislative solution is needed, what would be its main elements? Which activities of the beneficiary institutions should be covered and under which conditions?", "OPEN")
            self.putQuestion("If your view is that a different solution is needed, what would it be?", "OPEN")
            self.putQuestion("(a) [In particular if you are an institutional user:] Have you experienced specific problems when trying to negotiate agreements with rights holders that enable you to provide remote access, including across borders,  to your collections (or parts thereof) for purposes of research and private study? (b) [In particular if you are an end user/consumer:] Have you experienced specific problems when trying to consult, including across borders, works and other subject-matter held in the collections of institutions such as universities and national libraries when you are not on the premises of the institutions in question? (c) [In particular if you are a right holder:] Have you negotiated agreements with institutional users that enable those institutions to provide remote access, including across borders,  to the works or other subject-matter in their collections, for purposes of research and private study?", "OPEN")
            self.putQuestion("If there are problems, how would they best be solved?", "OPEN")
            self.putQuestion("If your view is that a legislative solution is needed, what would be its main elements? Which activities of the beneficiary institutions should be covered and under which conditions?", "OPEN")
            self.putQuestion("If your view is that a different solution is needed, what would it be?", "OPEN")
            self.putQuestion("(a) [In particular if you are a library:] Have you experienced specific problems when trying to negotiate agreements to enable the electronic lending (e-lending), including across borders, of books or other materials held in your collection? (b) [In particular if you are an end user/consumer:] Have you experienced specific problems when trying to borrow books or other materials electronically (e-lending), including across borders, from institutions such as public libraries? (c) [In particular if you are a right holder:] Have you negotiated agreements with libraries to enable them to lend books or other materials electronically, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved? ", "OPEN")
            self.putQuestion("[In particular if you are an institutional user:] What differences do you see in the management of physical and online collections, including providing access to your subscribers? What problems have you encountered?", "OPEN")
            self.putQuestion("[In particular if you are a right holder:]  What difference do you see between libraries’ traditional activities such as on-premises consultation or public lending and activities such as off-premises (online, at a distance) consultation and e-lending? What problems have you encountered?", "OPEN")
            self.putQuestion("[In particular if you are an institutional user, engaging or wanting to engage in mass digitisation projects, a right holder, a collective management organisation:] Would it be necessary in your country to enact legislation to ensure that the results of the 2011 MoU (i.e. the agreements concluded between libraries and collecting societies) have a cross-border effect so that out of commerce works can be accessed across the EU?", "YES/NO/NO OPINION")
            self.putQuestion("Would it be necessary to develop mechanisms, beyond those already agreed for other types of content (e.g. for audio- or audio-visual collections, broadcasters’ archives)?", "YES/NO/NO OPINION")
            self.putQuestion("(a) [In particular if you are an end user/consumer or an institutional user:] Have you experienced specific problems when trying to use works or other subject-matter for illustration for teaching, including across borders? (b) [In particular if you are a right holder:] Have you experienced specific problems resulting from the way in which works or other subject-matter are used for illustration for teaching, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved?", "OPEN")
            self.putQuestion("What mechanisms exist in the market place to facilitate the use of content for illustration for teaching purposes? How successful are they?", "OPEN")
            self.putQuestion("If your view is that a legislative solution is needed, what would be its main elements? Which activities of the beneficiary institutions should be covered and under what conditions?", "OPEN")
            self.putQuestion("If your view is that a different solution is needed, what would it be?", "OPEN")
            self.putQuestion("(a) [In particular if you are an end user/consumer or an institutional user:] Have you experienced specific problems when trying to use works or other subject matter in the context of research projects/activities, including across borders? (b) [In particular if you are a right holder:] Have you experienced specific problems resulting from the way in which works or other subject-matter are used in the context of research projects/activities, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved? ", "OPEN")
            self.putQuestion("What mechanisms exist in the Member States to facilitate the use of content for research purposes? How successful are they?", "OPEN")
            self.putQuestion("(a) [In particular if you are a person with a disability or an organisation representing persons with disabilities:] Have you experienced problems with accessibility to content, including across borders, arising from Member States’ implementation of this exception? (b) [In particular if you are an organisation providing services for persons with disabilities:] Have you experienced problems when distributing/communicating works published in special formats across the EU? (c) [In particular if you are a right holder:] Have you experienced specific problems resulting from the application of limitations or exceptions allowing for the distribution/communication of works published in special formats, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, what could be done to improve accessibility?", "OPEN")
            self.putQuestion("What mechanisms exist in the market place to facilitate accessibility to content? How successful are they?", "OPEN")
            self.putQuestion("(a) [In particular if you are an end user/consumer or an institutional user:] Have you experienced obstacles, linked to copyright, when trying to use text or data mining methods, including across borders? (b) [In particular if you are a service provider:] Have you experienced obstacles, linked to copyright, when providing services based on text or data mining methods, including across borders? (c) [In particular if you are a right holder:] Have you experienced specific problems resulting from the use of text and data mining in relation to copyright protected content, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved?", "OPEN")
            self.putQuestion("If your view is that a legislative solution is needed, what would be its main elements? Which activities should be covered and under what conditions?", "OPEN")
            self.putQuestion("If your view is that a different solution is needed, what would it be?", "OPEN")
            self.putQuestion("Are there other issues, unrelated to copyright, that constitute barriers to the use of text or data mining methods?", "OPEN")
            self.putQuestion("(a) [In particular if you are an end user/consumer:] Have you experienced problems when trying to use pre-existing works or other subject matter to disseminate new content on the Internet, including across borders? (b) [In particular if you are a service provider:] Have you experienced problems when users publish/disseminate new content based on the pre-existing works or other subject-matter through your service, including across borders? (c) [In particular if you are a right holder:] Have you experienced problems resulting from the way the users are using pre-existing works or other subject-matter to disseminate new content on the Internet, including across borders?", "YES/NO/NO OPINION")
            self.putQuestion("(a) [In particular if you are an end user/consumer or a right holder:] Have you experienced problems when trying to ensure that the work you have created (on the basis of pre-existing works) is properly identified for online use? Are proprietary systems sufficient in this context? (b) [In particular if you are a service provider:] Do you provide possibilities for users that are publishing/disseminating the works they have created (on the basis of pre-existing works) through your service to properly identify these works for online use?", "YES/NO/NO OPINION")
            self.putQuestion("(a) [In particular if you are an end user/consumer or a right holder):] Have you experienced problems when trying to be remunerated for the use of the work you have created (on the basis of pre-existing works)? (b) [In particular if you are a service provider:] Do you provide remuneration schemes for users publishing/disseminating the works they have created (on the basis of pre-existing works) through your service?", "YES/NO/NO OPINION")
            self.putQuestion("If there are problems, how would they best be solved?", "OPEN")
            self.putQuestion("If your view is that a legislative solution is needed, what would be its main elements? Which activities should be covered and under what conditions?", "OPEN")
            self.putQuestion("If your view is that a different solution is needed, what would it be?", "OPEN")
            self.putQuestion("In your view, is there a need to clarify at the EU level the scope and application of the private copying and reprography exceptions1 in the digital environment?", "YES/NO/NO OPINION")
            self.putQuestion("Should digital copies made by end users for private purposes in the context of a service that has been licensed by rightholders, and where the harm to the rightholder is minimal, be subject to private copying levies?1", "YES/NO/NO OPINION")
            self.putQuestion("How would changes in levies with respect to the application to  online services (e.g. services based on cloud computing  allowing, for instance, users to have copies on different devices) impact the development and functioning of new business models on the one hand and rightholders’ revenue on the other?", "OPEN")
            self.putQuestion("Would you see an added value in making levies visible on the invoices for products subject to levies?1", "YES/NO/NO OPINION")
            self.putQuestion("Have you experienced a situation where a cross-border transaction resulted in undue levy payments, or duplicate payments of the same levy, or other obstacles to the free movement of goods or services?", "YES/NO/NO OPINION")
            self.putQuestion("What percentage of products subject to a levy is sold to persons other than natural persons for purposes clearly unrelated to private copying? Do any of those transactions result in undue payments? Please explain in detail the example you provide (type of products, type of transaction, stakeholders, etc.).", "OPEN")
            self.putQuestion("Where such undue payments arise, what percentage of trade do they affect? To what extent could a priori exemptions and/or ex post reimbursement schemes existing in some Member States help to remedy the situation?", "OPEN")
            self.putQuestion("If you have identified specific problems with the current functioning of the levy system, how would these problems best be solved?", "OPEN")
            self.putQuestion("[In particular if you are an author/performer:] What is the best mechanism (or combination of mechanisms) to ensure that you receive an adequate remuneration for the exploitation of your works and performances?", "OPEN")
            self.putQuestion("Is there a need to act at the EU level (for instance to prohibit certain clauses in contracts)?", "YES/NO/NO OPINION")
            self.putQuestion("If you consider that the current rules are not effective, what would you suggest to address the shortcomings you identify?", "Open")
            self.putQuestion("Should the civil enforcement system in the EU be rendered more efficient for infringements of copyright committed with a commercial purpose?", "YES/NO/NO OPINION")
            self.putQuestion("In particular, is the current legal framework  clear enough to allow for  sufficient involvement of intermediaries (such as Internet service providers, advertising brokers, payment service providers, domain name registrars, etc.) in inhibiting online copyright infringements with a commercial purpose? If not, what measures would be useful to foster the cooperation of intermediaries?", "OPEN")
            self.putQuestion("Does the current civil enforcement framework ensure that the right balance is achieved between the right to have one’s copyright respected and other rights such as the protection of private life and protection of personal data?", "YES/NO/NO OPINION")
            self.putQuestion("Should the EU pursue the establishment of a single EU Copyright Title, as a means of establishing a consistent framework for rights and exceptions to copyright across the EU, as well as a single framework for enforcement?", "YES/NO/NO OPINION")
            self.putQuestion("Should this be the next step in the development of copyright in the EU? Does the current level of difference among the Member State legislation mean that this is a longer term project?", "OPEN")
            self.putQuestion("Are there any other important matters related to the EU legal framework for copyright? Please explain and indicate how such matters should be addressed.", "OPEN")
            self.save()

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
        self.conn.commit()


def test():
    """Tests the database handling by creating the database file
    with the defined schema"""

    db = Database()
    
    for i in db.listQuestions():
        print(i)
        input()
    
if __name__ == "__main__":
    test()

