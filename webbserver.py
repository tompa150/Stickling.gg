from flask import Flask, render_template, request
import psycopg2
app = Flask(__name__)


def read_user_info():
    conn_str = "dbname=server user= password= host=pgserver.mau.se port=5432"
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT email, username, password, number FROM user_info;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

@app.route("/register/")
def register():
    return render_template("register.html")

@app.route("/register_user/")
def register():
    email = getattr(request.forms, "Email")
    username = getattr(request.forms, "Användarnamn")
    password = getattr(request.forms, "Lösenord")
    conf_password = getattr(request.forms, "Bekräfta lösenord")
    number = getattr(request.forms, "Telefonnummer")
    user_info = read_user_info()
    for row in user_info:
        if email == row[0]:
            invalid_email = "Email already exists"
            return render_template("register.html", invalid_email = invalid_email)
        elif username == row[1]:
            invalid_username = "Username already exists"
            return render_template("register.html", invalid_username=invalid_username)
        elif password == row[2]:
            invalid_password = "Password alredy exists"
            return render_template("register.html", invalid_password = invalid_password)
        elif password != conf_password:
            non_similar_pass = "Your password is not the same, please re-enter your password."
            return render_template("register.html", non_similar_pass = non_similar_pass)
        elif number == row[3]:
            number_exists = "That number already exists, please enter your own number!"
            return render_template("register.html", number_exists = number_exists)
        
app.run(host="127.0.0.1", port=8080, debug=True)