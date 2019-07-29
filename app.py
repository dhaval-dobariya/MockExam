import flask
from main import newUserSignUp
from main import login
from authenticate import refreshAuthToken

app = flask.Flask('functions')

@app.route('/newUserSignUp', methods=['POST'])
def registerUser():
    return newUserSignUp(flask.request)

@app.route('/login', methods=['POST'])
def loginUser():
    return login(flask.request)

@app.route('/refreshAuthToken', methods=['POST'])
def refreshToken():
    return refreshAuthToken(flask.request)


if __name__ == '__main__':
    app.run()
