# [START User def]
class User(object):
   
    def __init__(self, id, firstName, lastName, email, password='', userId='', status='NEW', sysState='OPEN', dateCreated='', dateEdited='', createdBy='', editedBy=''):
        
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
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
    
    def to_dict(self, includePassword = False):

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

        if includePassword:
            dest['password'] = self.password

        return dest

# [END User def]
