import configparser
import os
from flask import flash, Flask, redirect, render_template, request, session, url_for
from utils import db_utils


app = Flask(__name__, static_folder="../static", template_folder="../templates")

app.secret_key = os.urandom(24)

# app.register_blueprint(sentiment_blueprint)

config_path = "../config.ini"
config = configparser.ConfigParser()
config.read(config_path)
config = {section:dict(config.items(section)) for section in config.sections()}
# app.config = config
print(f"Project Configurations: {config}")

engine = db_utils.get_engine(config['DATABASE'])

db_utils.setup(engine, config['DATABASE'])


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    users_table = config['DATABASE']['users_table']
    # get user login data and pass the data to utils
    name = request.form.get('uname')
    email = request.form.get('uemail')
    email = email.lower()
    password = request.form.get('upassword')
    # valid_password = password_check(password)
    # if valid_password:
    try:
        results = engine.execute(f"""SELECT * from {users_table} WHERE email='{email}'""")
        users = results.fetchall()
        print(f"======These are the users: {users}======")
        if len(users) > 0:
            flash("User already exists!!")
            return redirect(url_for('register'))
        else:
            engine.execute(f"""INSERT INTO {users_table} (name,email,password) VALUES 
                    ('{name}','{email}','{password}')""")
            return "User successfully registered!!"
    except Exception as e:
        flash("An error occurred during registering a user")
        print(f"An Exception occurred during adding a user: {str(e)}")
        return "An error occurred during registering a user"
    # else:
    #     flash("Password must follow strong password rules")
    #     return "Password format doesn't match the rules"


@app.route('/login_validation', methods=['POST'])
def login_validation():
    users_table = config['DATABASE']['users_table']
    email = request.form.get('Email')
    email = email.lower()
    password = request.form.get('Password')
    results = engine.execute(
        f"""SELECT * from {users_table} WHERE email='{email}' AND password='{password}'""")
    users = results.fetchall()
    # check if a user has already logged in
    print(email,password)
    if len(users) > 0:
        session['user_id'] = users[0][0]
        return redirect('/home')
    else:
        print("No user found!!")
        flash("No User Found for the provided email/password combination!!")
        return redirect('/')


@app.route('/logout')
def logout():
    # close the session
    session.pop('user_id')
    return redirect('/')
