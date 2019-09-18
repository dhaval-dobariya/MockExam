from google.cloud import firestore

# [START User def]
class User(object):
   
    def __init__(self, id, firstName, lastName, email, location = firestore.GeoPoint(0.0 ,0.0), password='', userId='', status='NEW', sysState='OPEN', dateCreated='', dateEdited='', createdBy='', editedBy=''):
        
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.location = location
        self.password = password
        self.userId = userId
        self.status = status
        self.sysState = sysState
        self.dateCreated = dateCreated
        self.dateEdited = dateEdited
        self.createdBy = createdBy
        self.editedBy = editedBy

    @staticmethod
    def from_dict(source):

        user = User(source['id'], source['firstName'], source['lastName'], source['email'])
    
        if 'location' in source:
            user.location = source['location']

        if 'password' in source:
            user.password = source['password']

        if 'userId' in source:
            user.userId = source['userId']
        
        if 'status' in source:
            user.status = source['status']
        
        if 'sysState' in source:
            user.sysState = source['sysState']
        
        if 'dateCreated' in source:
            user.dateCreated = source['dateCreated']
        
        if 'dateEdited' in source:
            user.dateEdited = source['dateEdited']

        if 'createdBy' in source:
            user.createdBy = source['createdBy']

        if 'editedBy' in source:
            user.editedBy = source['editedBy']

        return user
    
    def to_dict(self, isRequireLatLongDict = False, includePassword = False):

        dest = {
                'id' : self.id,
                'firstName' : self.firstName,
                'lastName' : self.lastName,
                'email' : self.email,
                'userId' : self.userId or '',
                'status' : self.status or '',
                'sysState' : self.sysState or '',
                'dateCreated' : self.dateCreated or '',
                'dateEdited' : self.dateEdited or '',
                'createdBy' : self.createdBy or '',
                'editedBy' : self.editedBy or ''
            }

        if isRequireLatLongDict:
            dest['location'] = {
                    'lat' : self.location.latitude,
                    'long': self.location.longitude
                } 


        if includePassword:
            dest['password'] = self.password

        return dest

# [END User def]

# [START Option def]
class Option(object):
   
    def __init__(self, index, option):
        self.index = index
        self.option = option


    @staticmethod
    def from_dict(source):
        option = Option(source['index'], source['option'])

        return option
    
    def to_dict(self):

        dest = {
                'index' : self.index,
                'option' : self.option
            }
            
        print('optionDict dest : ', dest)

        return dest

# [END Option def]

# [START Question def]
class Question(object):
   
    def __init__(self, question, options, correctAnswer, maxAllowedTime):
        
        self.question = question
        self.options = options
        self.correctAnswer = correctAnswer
        self.maxAllowedTime = maxAllowedTime

    @staticmethod
    def from_dict(source):

        optionsArray = source['options']
        options = []

        for optionDict in optionsArray:
            # print('optionDict : ', optionDict)

            option = Option.from_dict(optionDict)
            options.append(option)

        # print('options : ', options)

        question = Question(source['question'], options, source['correctAnswer'], source['maxAllowedTime'])

        # print('question : ', question)

        return question
    
    def to_dict(self):

        optionsDicts = []
        for option in self.options:
            optionsDicts.append(option.to_dict())

        print('optionsDicts : ', optionsDicts)


        dest = {
                'question' : self.question,
                'options' : optionsDicts,
                'correctAnswer' : self.correctAnswer,
                'maxAllowedTime' : self.maxAllowedTime or ''
            }

        return dest

# [END Question def]

# [START Subject def]
class Subject(object):
   
    def __init__(self, id, subject, questions, status='NEW', sysState='OPEN', dateCreated='', dateEdited='', createdBy='', editedBy=''):
        
        self.id = id
        self.subject = subject
        self.questions = questions
        self.status = status
        self.sysState = sysState
        self.dateCreated = dateCreated
        self.dateEdited = dateEdited
        self.createdBy = createdBy
        self.editedBy = editedBy

    @staticmethod
    def from_dict(source):

        questionsArray = source['questions']

        questions = []

        for questionDict in questionsArray:
            print('questionDict : ', questionDict)
            question = Question.from_dict(questionDict)
            questions.append(question)

        # print('questions : ', questions)

        # print('---- source : ', source)

        subject = Subject(source['id'], source['subject'], questions)
    
        if 'status' in source:
            subject.status = source['status']
        
        if 'sysState' in source:
            subject.sysState = source['sysState']
        
        if 'dateCreated' in source:
            subject.dateCreated = source['dateCreated']
        
        if 'dateEdited' in source:
            subject.dateEdited = source['dateEdited']

        if 'createdBy' in source:
            subject.createdBy = source['createdBy']

        if 'editedBy' in source:
            subject.editedBy = source['editedBy']

        print('subject : ', subject)

        return subject
    
    def to_dict(self):
        print('---- self : ', self)
        print('---- questions : ', self.questions)

        questionsDicts = []
        for question in self.questions:
            questionsDicts.append(question.to_dict())

        print('---- questionsDicts : ', questionsDicts)

        dest = {
                'id' : self.id,
                'subject' : self.subject,
                'questions' : questionsDicts,
                'status' : self.status or '',
                'sysState' : self.sysState or '',
                'dateCreated' : self.dateCreated or '',
                'dateEdited' : self.dateEdited or '',
                'createdBy' : self.createdBy or '',
                'editedBy' : self.editedBy or ''
            }

        return dest

# [END Subject def]
