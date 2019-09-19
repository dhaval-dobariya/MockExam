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
import pygeohash as pgh
import math
from geolocation import GeoLocation

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
                lat = request.json['location']['lat']
                long = request.json['location']['long']
                print("lat ", lat)
                print("long ", long)
                user.location = firestore.GeoPoint(lat, long)
                user.geohash = pgh.encode(lat, long)


            user.password = passwordHash
            user.dateCreated = firestore.SERVER_TIMESTAMP
            user.createdBy = user.email
            user.userId = user.email
            print("user to_dict ", user.to_dict(isRequireGeoPoint=True, includePassword=True))

            domain = user.email.split('@')[1] 
            print("domain ", domain)

            userDict = user.to_dict(isRequireGeoPoint=True, includePassword=True)

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
        # ~1 mile of lat and lon in degrees
        lat = 0.0144927536231884
        lon = 0.0181818181818182
        distance = request.json["distance"]

        if "location" in request.json:
            latitude = request.json["location"]["lat"]
            longitude = request.json["location"]["long"]

        lowerLat = latitude - (lat * distance)
        lowerLon = longitude - (lon * distance)

        greaterLat = latitude + (lat * distance)
        greaterLon = longitude + (lon * distance)

        print("lowerLat lowerLon", lowerLat, lowerLon)  
        print("greaterLat greaterLon", greaterLat, greaterLon)  

        lesserGeopoint = firestore.GeoPoint(lowerLat, lowerLon)
        greaterGeopoint = firestore.GeoPoint(greaterLat, greaterLon)

        lesserGeoHash = pgh.encode(lowerLat, lowerLon, precision=5)
        greaterGeoHash = pgh.encode(greaterLat, greaterLon, precision=5)

        print("lesserGeoHash ", lesserGeoHash)            
        print("greaterGeoHash ", greaterGeoHash)            

        userQueryRef = usersCollectionRef
        userQueryRef = userQueryRef.where('sysState', '==', 'OPEN')
        # userQueryRef.where('location', '>', lesserGeopoint).where('location', '<', greaterGeopoint)

        userQueryRef = userQueryRef.where('geohash', '>=', lesserGeoHash).where('geohash', '<', greaterGeoHash)
        userQueryRef = userQueryRef.order_by('geohash')

        docs = userQueryRef.limit(20).get()

        users = []
        for doc in docs:
            user = User.from_dict(doc.to_dict())

            # To Filter out extra results 
            userLatLong = GeoLocation.from_degrees(user.location.latitude, user.location.longitude)
            requestedUserLatLong = GeoLocation.from_degrees(latitude, longitude)
            distanceBetweenUsers = userLatLong.distance_to(requestedUserLatLong)
            print("distanceBetweenUsers ", distanceBetweenUsers)
            print("user.geohash ", user.geohash)

            if distanceBetweenUsers <= distance:
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
    except Exception as e:
        return flask.jsonify({
                         'message': 'Something went wrong!!' + str(e)
                         })


