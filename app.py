import flask
import main
import authenticate
import subject

app = flask.Flask('functions')

@app.route('/newUserSignUp', methods=['POST'])
def registerUser():
    return main.newUserSignUp(flask.request)

@app.route('/login', methods=['POST'])
def loginUser():
    return main.login(flask.request)

@app.route('/refreshAuthToken', methods=['POST'])
def refreshToken():
    return authenticate.refreshAuthToken(flask.request)

@app.route('/subject', methods=['GET','POST'])
def subjects():
    if flask.request.method == 'POST':
        return subject.createSubject(flask.request)
    elif flask.request.method == 'GET':
        return subject.getSubjects()

if __name__ == '__main__':
    app.run()
