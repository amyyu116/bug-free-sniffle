import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response,
    redirect,
    url_for
)
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod"


class User(db.Model):
    # creates table
    __tablename__ = "users_b"

    # stores values into table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    # stores emails. constructor?
    def __init__(self, email):
        self.email = email


@app.route("/")
def root():
    print_debug_info()
    '''
    text = 'hello cs40'
    text = '<strong>' + text + '</strong>' # + 100
    return text
    '''
    messages = [{}]

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    print(username)
    print(password)
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # render_template does preprocessing of the input html file;
    # technically, the input to the render_template function is in a language called jinja2
    # the output of render_template is html

    # display first 20 tweets
    sql = """
    SELECT text AS text, created_at
    FROM tweets
    ORDER BY created_at DESC
    LIMIT 20;
    """
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    result = connection.execute(text(sql))
    for row in result:
        messages.append({'text': row.text, 'created_at': row.created_at})
    return render_template('root.html', logged_in=good_credentials, messages=messages)


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    # FIXME:
    # look inside the databasse and check if the password is correct for the user
    if username == 'haxor' and password == '1337':
        return True
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    # requests (plural) library for downloading;
    # now we need request singular
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            # return 'login successful'
            # create a cookie that contains the username/password info

            template = render_template(
                'login.html',
                bad_credentials=False,
                logged_in=True)
            # return template
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response


@app.route('/logout')
def logout():
    # Create a response to redirect to the login page
    # Clear the username and password cookies

    response = make_response(render_template('root.html', logged_in=False))
    response.set_cookie('username', '', expire=0)
    response.set_cookie('password', '', expire=0)
    return response


@app.route("/create_account")
def create_account():
    return render_template('create_account.html')


@app.route("/create_message")
def create_message():
    return 'create message page'


@app.route('/search', methods=['GET', 'POST'])
def search():
    # keyWord = request.args.get('search')

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    return render_template('search.html', logged_in=good_credentials)


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
