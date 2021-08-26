import hmac
import sqlite3

import mail
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader

# create class (object) for Database functions
class Database(object):
    # function to connect to Database and crete cursor
    def __init__(self):
        self.conn = sqlite3.connect('store.db')
        self.cursor = self.conn.cursor()

    # function for INSERT AND UPDATE query
    def commiting(self, query, values):
        self.cursor.execute(query, values)
        self.conn.commit()

    # function for executing SELECT query
    def single_commiting(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    # function to fetch data for SELECT query
    def fetching(self):
        return self.cursor.fetchall()

    def select_product(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

# return response with names of columns in the table
def dict_factory(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary

def image_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name ="djcpeeu7k", api_key="168276427645577",
                      api_secret="z7qzuUnTfhyh9ylrxV0UXM_SvPc")
    upload_result = None
    if request.method == 'POST' or request.method =='PUT':
        image = request.json['product_image']
        app.logger.info('%s file_to_upload', image)
        if image:
            upload_result = cloudinary.uploader.upload(image)
            app.logger.info(upload_result)
            return upload_result['url']


# Function to create users table
def init_user_table():
    conn = sqlite3.connect('store.db')
    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "physical_address TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("users table created successfully")
    conn.close()

# Function to create product table
def init_product_table():
    with sqlite3.connect('store.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS user_products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_id INTEGER NOT NULL,"
                     "product_name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES user (user_id))")
    print("user's product table created successfully.")


init_user_table()
init_product_table()


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'abdullah.isaacs@gmail.com'
app.config['MAIL_PASSWORD'] = 'yolo0909!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['CORS_HEADERS'] = ['Content-Type']

@app.route('/', methods=["GET"])
def welcome():
    response = {}
    if request.method == "GET":
        response["message"] = "Welcome"
        response["status_code"] = 201
        return response

@app.route('/user/', methods=["POST", "GET", "PATCH"])
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    # Login function
    if request.method == "PATCH":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect("store.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password,))
            user = cursor.fetchone()
            if user != None:
                response['status_code'] = 200
                response['data'] = user
                return response
            else:
                return "user does not exist"

    # registration
    if request.method == "POST":
        name = request.form['name']
        last_name = request.form['last_name']
        username = request.form['username']
        physical_address = request.form['physical_address']
        email = request.form['email']
        password = request.form['password']
        if (re.search(regex, email)):
            with sqlite3.connect("store.db") as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE email='" + email + "'")
                user = cursor.fetchone()
                if user == None:
                    with sqlite3.connect("store.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO user("
                                       "name,"
                                       "last_name,"
                                       "username,"
                                       "physical_address,"
                                       "email,"
                                       "password) VALUES(?, ?, ?, ?, ?, ?)",
                                       (name, last_name, username, physical_address, email, password))
                        conn.commit()
                        mail=Mail()
                        msg = Message('Successfully registered', sender='abdullah.isaacs@gmail.com', recipients=[email])
                        msg.body = "Welcome to the future"
                        mail.send(msg)
                        response["message"] = "success"
                        response["status_code"] = 201

                        return response
                else:
                    return "user already exists"
        else:
            return "PLease enter a valid email"

# view profile
@app.route('/user/<email>', methods=["GET","PUT"])
def get_user(email):
    response = {}
    db = Database()

    # fetch specific user
    if request.method == "GET":
        with sqlite3.connect("store.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email='" + email + "'")
            user = cursor.fetchone()
            if user != None:
                response['status_code'] = 200
                response['data'] = user
                return response
            else:
                return "User does not exist"

    # update specific profile
    if request.method == "PUT":
        name = request.form['name']
        last_name = request.form['last_name']
        username = request.form['username']
        physical_address = request.form['physical_address']
        email = request.form['email']
        password = request.form['password']

        query = "UPDATE user SET name=?, last_name=?, username=?, physical_address, email=?, password=?" \
                " WHERE email='" + email + "'"
        values = name, last_name, username, physical_address, email, password

        db.commiting(query, values)

        if email != None:
            response['message'] = 200
            response['message'] = "Profile successfully updated "

            return response
        else:
            return "user does not exist"


# create end-point to delete user
@app.route("/delete-profile/<email>")

def delete_profile(email):

    response = {}
    db = Database()

    query = "DELETE FROM user WHERE email='" + email + "'"
    db.single_commiting(query)
    #error handling to check if the id exists
    if email == []:
        return "user does not exist"
    else:
        response['status_code'] = 200
        response['message'] = "profile deleted successfully."
        return response


if __name__ == '__main__':
    app.debug = True
    app.run()