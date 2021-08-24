import hmac
import sqlite3
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import re
import cloudinary
import cloudinary.uploader



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

init_user_table()


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

@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if request.method == "POST":
        name = request.form['name']
        last_name = request.form['last_name']
        username = request.form['username']
        physical_address = request.form['physical_address']
        email = request.form['email']
        password = request.form['password']
        if (re.search(regex, email)):
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

                response["message"] = "success. message sent"
                response["status_code"] = 201

                return response
        else:
            return "PLease enter a valid email"


if __name__ == '__main__':
    app.run(debug=True)
