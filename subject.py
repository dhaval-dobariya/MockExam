from google.cloud import firestore
import flask
import json
from models import Subject

db = firestore.Client()

subjectsCollectionRef = db.collection('subjects')

# Add new subject with questions
def createSubject(request):

    try:

        try:
            json_data = json.dumps({
                                "subject": request.json['subject'],
                                "questions": request.json['questions'],
                                  })
        except:
            return flask.jsonify({
                                 'status': 300,
                                 'message': 'Invalid request body!'
                                 })

        docs = subjectsCollectionRef.where('subject', '==', request.json['subject']).where('sysState', '==', 'OPEN').limit(1).get()

        firstDoc = None
        for doc in docs:
            firstDoc = doc

        if firstDoc is not None:

            return flask.jsonify({
                         'status' : 201,
                         # 'data' : firstDoc.to_dict(),
                         'message' : 'Subject already exist!! With id ' + firstDoc.id
                         })
        else:

            docRef = subjectsCollectionRef.document()

            newDocId = docRef.id

            request.json["id"] = newDocId

            subject = Subject.from_dict(request.json)

            subject.dateCreated = firestore.SERVER_TIMESTAMP
            # subject.createdBy = createdBy

            subjectsCollectionRef.document(newDocId).set(subject.to_dict())
              
            return flask.jsonify({
                                 'status': 200,
                                 'message': 'Subject created successfully!!'
                                 })  
    except:
        return flask.jsonify({
                             'status': 301,
                             'message': 'Something went wrong!!'
                             })

# Get all subjects with questions
def getSubjects():
    
    try:

        docs = subjectsCollectionRef.where('sysState', '==', 'OPEN').limit(20).get()

        subjects = []
        for doc in docs:
            subjects.append(doc.to_dict())

        if subjects is not None:

            return flask.jsonify({
                         'status': 200,
                         'data': subjects,
                         'message': 'Subjects details successfully retrived!!'
                         })
        else:
            return flask.jsonify({
                         'message': 'Subjects not found!!'
                         })
    except:
        return flask.jsonify({
                         'message': 'Something went wrong!!'
                         })