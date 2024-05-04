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
db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev"


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
    connection.close()
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
    username_found = False
    sql = """
    SELECT screen_name, password
    FROM users
    WHERE screen_name = :username AND
          password = :password
    LIMIT 1;
    """
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    result = connection.execute(text(sql), {"username":username, "password":password})
    for row in result:
        if row.screen_name == username and row.password == password:
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
        good_credentials = are_credentials_good(username, password)
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

    response = make_response(render_template('logout.html'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    return response


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]
        if password_confirm == password and username is not None:
            # generate a new user_id....
            new_id = generate_user_id()
            sql = """
            INSERT INTO users (screen_name, id_users, password)
            VALUES (:username, :new_id, :password)
            """
            engine = sqlalchemy.create_engine(db_connection)
            connection = engine.connect()
            transaction = connection.begin()
                # Execute the SQL query
            connection.execute(text(sql), {"username": username, "new_id": new_id,
                                            "password": password})
            connection.commit()
                # Insertion successful
            return redirect(url_for("login"))
            connection.close()
        else:
            return render_template('create_account.html', bad_credentials=True)
    else:
        return render_template('create_account.html', bad_credentials=False)

def generate_user_id():
    # Generate a new user_id
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    new_id=0
    while True:
        # Generate a random new_id
        new_id+=1
        # Check if new_id already exists in the database
        sql = """
        SELECT COUNT(*)
        FROM users
        WHERE id_users = :new_id
        """
        result = connection.execute(text(sql), {"new_id": new_id}).scalar()
        if result == 0:
            # new_id is unique, break the loop
            break
    return new_id

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
