
import sqlite3

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
        self.conn = sqlite3.connect('backend.db')
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
        image = request.json['image']
        app.logger.info('%s file_to_upload', image)
        if image:
            upload_result = cloudinary.uploader.upload(image)
            app.logger.info(upload_result)
            return upload_result['url']


# Function to create users table
def init_user_table():
    conn = sqlite3.connect('backend.db')
    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "physical_address TEXT NOT NULL,"
                 "email TEXT NOT NULL UNIQUE,"
                 "password TEXT NOT NULL)")
    print("users table created successfully")
    conn.close()

# Function to create product table
def init_product_table():
    with sqlite3.connect('backend.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS all_products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "email INTEGER NOT NULL,"
                     "product_name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "type TEXT NOT NULL,"
                     "FOREIGN KEY (email) REFERENCES user (email))")
    print(" all_products table created successfully.")


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

@app.route('/user/', methods=["POST", "PATCH"])
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    # Login function
    if request.method == "PATCH":
        email = request.json["email"]
        password = request.json["password"]

        with sqlite3.connect("backend.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password,))
            user = cursor.fetchone()
            if user != None:
                response['status_code'] = 200
                response['data'] = user
                return response
            else:
                response['status_code'] = 404
                response['data'] = "User not found"
                return response

    # registration
    if request.method == "POST":
        name = request.json['name']
        last_name = request.json['last_name']
        username = request.json['username']
        physical_address = request.json['physical_address']
        email = request.json['email']
        password = request.json['password']

        if re.search(regex, email):
            with sqlite3.connect("backend.db") as conn:
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
                # mail = Mail(app)
                # msg = Message('Successfully registered', sender='abdullah.isaacs@gmail.com', recipients=[email])
                # msg.body = "Welcome to the future"
                # mail.send(msg)
                response["message"] = "success"
                response["status_code"] = 201

                return response

        else:
            response['status_code'] = 400
            response["message"] = "Email did not pass regex"
            return response

# view profile
@app.route('/user/<email>', methods=["GET","PUT"])
def get_user(email):
    response = {}
    db = Database()

    # fetch specific user
    if request.method == "GET":
        with sqlite3.connect("backend.db") as conn:
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
        name = request.json['name']
        last_name = request.json['last_name']
        username = request.json['username']
        physical_address = request.json['physical_address']
        email = request.json['email']
        password = request.json['password']

        query = "UPDATE user SET name=?, last_name=?, username=?, physical_address=?, email=?, password=?" \
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


# products section

@app.route("/product-table/", methods=["POST","GET"])

def add():

    response = {}
    db = Database()

    if request.method == "POST":
        email = request.json['email']
        product_name = request.json['product_name']
        description = request.json['description']
        price = request.json['price']
        prod_type = request.json['type']

        try:
            query = "INSERT INTO all_products(email, product_name, description, image, price, type) VALUES(?, ?, ?, ?, ?, ?)"
            values = email, product_name, description, price, image_file(), prod_type
            db.commiting(query, values)
            response["status_code"] = 201
            response['description'] = "item added successfully"

            return response

        except ValueError:
            return {
                "error": "failed to insert into DB"
            }

    # view all products
    if request.method == "GET":
        query = "SELECT * FROM  all_products"
        db.single_commiting(query)

        response['status_code'] = 200
        response['data'] = db.fetching()

        return response


@app.route("/view-product/<int:prod_id>")
def view(prod_id):
    response = {}
    db = Database()

    if request.method == "GET":
        query = "SELECT * FROM  all_products WHERE prod_id=" + str(prod_id)
        db.single_commiting(query)

        response['status_code'] = 200
        response['data'] = db.fetching()

        return response




# create end-point to edit existing products/
@app.route("/updating-products/<int:prod_id>", methods=["PUT","GET"])

def edit(prod_id):

    response = {}
    db = Database()

    if request.method == "PUT":
        email = request.json['email']
        product_name = request.json['product_name']
        description = request.json['description']
        price = request.json['price']
        prod_type = request.json['type']
        try:
            testp = int(price)

            query = "UPDATE all_products SET email=?, product_name=?, description=?, image=?, price=?, type=?" \
                    " WHERE prod_id='" + str(prod_id) + "'"
            values = email, product_name, description, price, image_file(), prod_type

            db.commiting(query, values)

            response['message'] = 200
            response['message'] = "Product successfully updated "

            return response

        except ValueError:
            return "Please enter integer values for price and quantity"

    #     delete product
    if request.method == "GET":
        query = "DELETE FROM all_products WHERE prod_id=" + str(prod_id)
        db.single_commiting(query)
        # error handling to check if the id exists
        if id == []:
            return "product does not exist"
        else:
            response['status_code'] = 200
            response['message'] = "item deleted successfully."
            return response


# fetch specific user's products
@app.route('/products/<email>', methods=["GET"])
def get_user_products(email):
    response = {}

    # fetch specific user
    if request.method == "GET":
        with sqlite3.connect("backend.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM all_products WHERE email='" + email + "'")
            user = cursor.fetchall()
            if user != None:
                response['status_code'] = 200
                response['data'] = user
                return response
            else:
                return "incorrect email, no products to fetch"


if __name__ == '__main__':
    app.debug = True
    app.run()