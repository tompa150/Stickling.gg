from flask import Flask, render_template, request, url_for
import psycopg2
app = Flask(__name__, template_folder='HTML')

username = None
password = None

def read_user_info():
    conn_str = "dbname=server user= password= host=pgserver.mau.se port=5432"
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT email, username, password, number FROM user_info;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

app.route("/login/")
def login():
    return render_template("login.html")

app.route("/validation/",methods = ['POST'])
def validation():
    global username 
    global password
    username = getattr(request.form, "Användarnamn")
    password = getattr(request.form, "Lösenord")
    user_info = read_user_info()
    for row in user_info:
        if username == row[1] and password == row[2]:
            return render_template("homepage.html")
        elif username != row[1] and password == row[2]:
            wrong_user = "Felaktigt användarnamn, vänligen ange ett giltigt sådant."
            return render_template("login.html", wrong_user = wrong_user)
        elif username == row[1] and password != row[2]:
            wrong_pass = "Lösenordet är inkorrekt, vänligen ange ett giltigt lösenord"
            return render_template("login.html", wrong_pass = wrong_pass)
        else:
            wrong_user_pass = "Både användarnamn och lösenord är felaktiga, vänligen ange ett giltigt input"
            return render_template("login.html", wrong_user_pass = wrong_user_pass)

            
       
@app.route("/register/")
def register():
    return render_template("register.html")


@app.route("/register_user/",methods = ['POST'])
def register_user():
    email = getattr(request.form, "Email")
    username = getattr(request.form, "Användarnamn")
    password = getattr(request.form, "Lösenord")
    conf_password = getattr(request.form, "Bekräfta lösenord")
    number = getattr(request.form, "Telefonnummer")
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

if __name__ == "__main__":      
    app.run(host="127.0.0.1", port=8080, debug=True)