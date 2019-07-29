import json
import flask
import jwt
import datetime
import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

VALID_AUTH_TOKEN_TIME = datetime.timedelta(days=0, minutes=60, seconds=0)
VALID_REFRESH_TOKEN_TIME = datetime.timedelta(days=30, minutes=00, seconds=0)

firebase_admin.initialize_app()

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

usersCollectionRef = db.collection('users')

def generateRefreshToken(email):
    payload = {
        'exp': datetime.datetime.utcnow() + VALID_REFRESH_TOKEN_TIME,
        'iat': datetime.datetime.utcnow(),
        'sub': email,
        'type': 'refreshToken'
    }

    print("generateRefreshToken payload", payload)
    print("SECRET_KEY ", os.getenv('SECRET_KEY'))

    refreshToken = jwt.encode(
        payload,
        os.getenv('SECRET_KEY'),
        algorithm='HS256'
    ).decode()

    return refreshToken


def refreshAuthToken(request):

    try:

        if "refreshToken" in request.json:

            # First check its valid Refresh token
            isValidRefreshToken = verifyAuthToken(request.json["refreshToken"])
            print("isValidRefreshToken : ", isValidRefreshToken)

            if isValidRefreshToken["status"] == 200:

                if 'type' in isValidRefreshToken["payload"]:
                    email = isValidRefreshToken["payload"]["sub"]

                    # If valid refresh token then fetch user id to generate new authToken
                    db = firestore.Client()

                    usersCollectionRef = db.collection('users')

                    userDocs = usersCollectionRef.where('email', '==', email).where('sysState', '==', 'OPEN').limit(
                        1).get()

                    userDoc = None
                    for doc in userDocs:
                        userDoc = doc.to_dict()

                    print('userDoc : ', userDoc)

                    if userDoc is not None:
                        userId = userDoc["id"]
                        tenantId = userDoc["tenantId"]

                        authToken = generateAuthToken(email, userId, tenantId)
                        print('authToken : ', authToken)

                    return flask.jsonify({
                        "status": 200,
                        "authToken": authToken
                    })
                else:
                    return flask.jsonify({
                        'status': 300,
                        'message': 'Invalid refresh token!'
                    })
            else:
                return flask.jsonify({
                    'status': isValidRefreshToken["status"],
                    'message': isValidRefreshToken["message"]
                })

        else:
            return flask.jsonify({
                'status': 300,
                'message': 'Invalid request body!'
            })

    except Exception as e:

        print("Exception : ", e)
        return flask.jsonify({
                    'status': 300,
                    'message': 'Invalid request body!'
                })


def generateAuthToken(email, userId):
    payload = {
        'exp': datetime.datetime.utcnow() + VALID_AUTH_TOKEN_TIME,
        'iat': datetime.datetime.utcnow(),
        'sub': email,
        'uid': userId,
    }

    print("generateAuthToken payload", payload)
    print("SECRET_KEY ", os.getenv('SECRET_KEY'))

    return jwt.encode(
        payload,
        os.getenv('SECRET_KEY'),
        algorithm='HS256'
    ).decode()


def verifyAuthToken(authToken):

    print("verifyAuthToken SECRET_KEY", os.getenv('SECRET_KEY'))
    print("verifyAuthToken authToken", authToken)

    try:
        payload = jwt.decode(authToken, os.getenv('SECRET_KEY'), "utf-8")
        print("verifyAuthToken payload", payload)

        return flask.jsonify({
                                "status": 200,
                                "payload": payload
                                }).json
    except jwt.ExpiredSignatureError:
        print('Signature expired. Please log in again.')
        return flask.jsonify({
            "status": 300,
            'message': 'Signature expired. Please log in again.'
        }).json
    except jwt.InvalidTokenError:
        print('Invalid token. Please log in again.')
        return flask.jsonify({
            "status": 301,
            'message': 'Invalid token. Please log in again.'
        }).json
