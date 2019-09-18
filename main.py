from google.cloud import firestore
import json
import flask
import firebase_admin
import jwt
import datetime
import os
from passlib.hash import pbkdf2_sha256
from random import randint
import authenticate
from authenticate import refreshAuthToken
from authenticate import generateAuthToken
from authenticate import generateRefreshToken
from models import User

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

usersCollectionRef = db.collection('users')

# New user signup
def newUserSignUp(request):

    try:

        if "email" not in request.json or "password" not in request.json:
            return flask.jsonify({
                                 'status': 300,
                                 'message': 'Invalid request body!'
                                 })

        print('request.json : ', request.json)
         
        # First check user exist or not        
        userDocs = usersCollectionRef.where('email', '==', request.json['email']).where('sysState', '==', 'OPEN').limit(1).get()

        userExistDoc = None
        for doc in userDocs:
            userExistDoc = doc

        print('userExistDoc : ',userExistDoc)

        if userExistDoc is not None:
            return flask.jsonify({
                                 'status': 201,
                                 'message': 'Email aleary exist!'
                                 })

        else:
            # If user not exist then register it
            passwordHash = pbkdf2_sha256.encrypt(request.json['password'], rounds=200000, salt_size=16)
            print("passwordHash ", passwordHash)

            docRef = usersCollectionRef.document()
            print("docRef ", docRef)

            newDocId = docRef.id
            print("newDocId ", newDocId)

            request.json["id"] = newDocId

            print("firestore.SERVER_TIMESTAMP ", firestore.SERVER_TIMESTAMP)

            user = User.from_dict(request.json)
            print("user ", user)

            if "location" in request.json:
                print("lat ", request.json['location']['lat'])
                print("long ", request.json['location']['long'])
                user.location = firestore.GeoPoint(request.json['location']['lat'], request.json['location']['long'])

            user.password = passwordHash
            user.dateCreated = firestore.SERVER_TIMESTAMP
            user.createdBy = user.email
            user.userId = user.email
            print("user to_dict ", user.to_dict())

            domain = user.email.split('@')[1] 
            print("domain ", domain)

            userDict = user.to_dict(includePassword=True)

            # Add user to Firestore
            usersCollectionRef.document(newDocId).set(userDict)

            # Generate token
            userAuthToken = authenticate.generateAuthToken(user.email, user.id)
            print("userAuthToken ", userAuthToken)

            # Generate refresh token
            refreshToken = authenticate.generateRefreshToken(user.email)
            print("refreshToken ", refreshToken)

            return flask.jsonify({
                "status": 200,
                'data': {
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'authToken': userAuthToken,
                    'refreshToken': refreshToken
                },
                "message": "You are successfully registered into Seed!!",
            })
            
    
    except:
        return flask.jsonify({
                             'status' : 301,
                             'message' : 'Something went wrong!!'
                             })

# User login
def login(request):

    try:
    
        try:
            json_data = json.dumps({
                                   "email" : request.json['email'],
                                   "password" : request.json['password'],
                                   })
        except:
            return flask.jsonify({
                         'status' : 300,
                         'message' : 'Invalid request body!'
                         })

        print('Login Input : ', json_data)
        
        docs = usersCollectionRef.where('email', '==', request.json['email']).where('sysState', '==', 'OPEN').limit(1).get()

        userDoc = None
        for doc in docs:
            userDoc = doc

        if userDoc is not None:
            userDict = userDoc.to_dict()
            print('userDict : ', userDict)

            # Verify password hash
            isValidPassword = pbkdf2_sha256.verify(request.json['password'], userDict['password'])
            print('isValidPassword : ', isValidPassword)

            if isValidPassword is False:
                return flask.jsonify({
                                 'status': 201,
                                 'message': 'Invalid email or password!'
                                 })
            else:

                responseDict = {
                                'status': 200,
                                'data': {
                                    'firstName': userDict["firstName"],
                                    'lastName': userDict["lastName"],
                                }
                               }

                # Generate token  
                userAuthToken = authenticate.generateAuthToken(userDict['email'], userDict['id'])
                responseDict['data']['authToken'] = userAuthToken

                # Generate refresh token
                refreshToken = authenticate.generateRefreshToken(userDict['email'])
                responseDict['data']['refreshToken'] = refreshToken

                responseDict['message'] = "User logged in!"
               
                return flask.jsonify(responseDict)
        else:
            return flask.jsonify({
                                 'status': 201,
                                 'message': 'Invalid email or password!'
                                 })
            
    except:
        return flask.jsonify({
                         'status': 301,
                         'message': 'Something went wrong!!'
                         })

# Get all nearby users
def getUsers(request):
    
    try:

        docs = usersCollectionRef.where('sysState', '==', 'OPEN').limit(20).get()

        users = []
        for doc in docs:
            user = User.from_dict(doc.to_dict())
            users.append(user.to_dict(isRequireLatLongDict = True))

        if users is not None:

            return flask.jsonify({
                         'status': 200,
                         'data': users,
                         'message': 'Users details successfully retrived!!'
                         })
        else:
            return flask.jsonify({
                         'message': 'Users not found!!'
                         })
    except:
        return flask.jsonify({
                         'message': 'Something went wrong!!'
                         })
