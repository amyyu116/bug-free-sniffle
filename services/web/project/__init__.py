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
    page = request.args.get('page', 1, type=int)
    num_messages = 20
    offset = (page - 1) * num_messages

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
    SELECT tweets.text AS text, users.screen_name, tweets.created_at
    FROM tweets
    JOIN users USING (id_users)
    ORDER BY created_at DESC, id_tweets DESC 
    LIMIT :limit OFFSET :offset;
    """
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    result = connection.execute(text(sql), {'limit': num_messages, 'offset': offset}).fetchall()
    for row in result:
        messages.append({'text': row.text, 'created_at': row.created_at, 'screen_name': row.screen_name})
    connection.close()
    return render_template('root.html', logged_in=good_credentials, messages=messages,page=page)


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
        engine = sqlalchemy.create_engine(db_connection)
        connection = engine.connect()
        username_unique = check_username(username)
        if password_confirm == password and username_unique:
            # generate a new user_id....
            sql = """
            INSERT INTO users (screen_name, password)
            VALUES (:username, :password)
            """
            transaction = connection.begin()
                # Execute the SQL query
            connection.execute(text(sql), {"username": username,
                                            "password": password})
            connection.commit()
                # Insertion successful
            return redirect(url_for("login"))
            connection.close()
        else:
            return render_template('create_account.html', bad_credentials=True)
    else:
        return render_template('create_account.html', bad_credentials=False)

def check_username(username):
    if username is None:
        return False
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    sql = """
        SELECT count(*) as count
        FROM users
        WHERE screen_name = :username;
    """
    result = connection.execute(text(sql), {"username": username})
    for row in result:
        if row.count == 0:
            return True
    connection.close()
    return False

@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # create message
    if request.method == 'POST':
        # removes trailing and ending whitespaces to check for empty input
        message = request.form.get('message').strip() if request.form.get('message') else ''
        print(message)
        if not message:  # No message was entered
           return render_template('create_message.html', returnMessage="No message provided.", logged_in=good_credentials)

        else:
            engine = sqlalchemy.create_engine(db_connection)
            connection = engine.connect()
            transaction = connection.begin()    
            try:
                id_users = get_user_id(username, password)
                print(id_users)
                sql = """
                INSERT INTO tweets (
                    id_users,
                    created_at, 
                    text
                    ) VALUES (
                    :id_users, 
                    NOW(), 
                    :message);
                """
                connection.execute(text(sql), {'id_users': id_users, 'message': message})
                transaction.commit()
                return render_template('create_message.html', returnMessage="Message successfully posted!", logged_in=good_credentials)
            except Exception as e:    
                transaction.rollback()
                raise e
    
    return render_template('create_message.html', logged_in=good_credentials)

def get_user_id(username, password):
    """
    This function is a helper function for create_message that 
    """
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    sql = """
        SELECT id_users FROM users WHERE screen_name = :username AND password = :password
        """
    result = connection.execute(text(sql), {"username": username, "password": password})
    # fetch the first column of the row (user id)
    user_id = result.scalar()
    return user_id


@app.route('/search', methods=['GET', 'POST'])
def search():
    # keyWord = request.args.get('search')

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    messages = [{}]
    page = request.args.get('page', 1, type=int)
    num_messages = 20
    offset = (page - 1) * num_messages
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)
    if request.method == 'POST':
        keyword = request.form.get('query')
        if keyword:
            engine = sqlalchemy.create_engine(db_connection)
            connection = engine.connect()
            sql = """
              SELECT tweets.text AS text, users.screen_name, tweets.created_at
            FROM tweets
            JOIN users USING (id_users)
            WHERE tweets.text ILIKE :keyword
            ORDER BY created_at DESC, id_tweets DESC
            LIMIT :limit OFFSET :offset;  
            """
            results = connection.execute(text(sql), {'limit': num_messages, 'offset': offset,'keyword':f'%{keyword}%'})
            for row in results:
                messages.append({'text': row.text, 'created_at': row.created_at, 'screen_name': row.screen_name})
            connection.close()
            return render_template('search.html', logged_in=good_credentials, messages=messages, searched=True, page=page) 
    return render_template('search.html', logged_in=good_credentials, messages=messages, searched=False)


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
    return
