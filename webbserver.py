from flask import Flask, render_template, request, url_for, session, g, redirect
import psycopg2
app = Flask(__name__, template_folder='HTML')
app.secret_key = "stickling.gg"

def new_ad_id():
    largest_id = 1
    ads = ad_read()
    for ad in ads:
        if ad[0] >= largest_id:
            largest_id = ad[0] + 1
    return largest_id

def read_user_info():
    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, email number FROM users;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def ad_read():
    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    cursor.execute(""" SELECT * FROM ads; """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def image_ad_read(user):
    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    cursor.execute(f""" SELECT ads.ad_id, ads.title, ads.description, images.image_path FROM ads JOIN images ON ads.ad_id = images.ad_id WHERE ads.username = {user} """)
    results = cursor.fetchall()
    ads = {}
    for row in results:
        ad_id = row[0]
        ad_title = row[1]
        ad_description = row[2]
        image_path = row[3]
        if ad_id not in ads:
            ads[ad_id] = {'title': ad_title, 'description': ad_description, 'image_paths': []}
        ads[ad_id]['images'].append(image_path)
        conn.close()
    return ads

def insert_image_path(images, ad_id):
    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    ad_id = new_ad_id()
    for path in images:
        cursor.execute(""" INSERT INTO images (image_path, ad_id) VALUES (?, ?) """, (path, ad_id) )
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return

def insert_ad(title, description, price, type, username, image_paths):
    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    ad_id = new_ad_id()
    cursor.execute(f""" INSERT into ads(ad_id, username, title, price, description, ad_type) VALUES ({ad_id}, {username}, {title}, {price}, {description}); """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    if image_paths == "":
        return
    else:
        insert_image_path(image_paths, ad_id)
        return

@app.route("/profile/")
def profile():
    if g.user:
        user = session['user']
        user_info = read_user_info()
        for one_user in user_info:
            if user == one_user[0]:
                user_ads = image_ad_read(user)
                return render_template("profile.html", one_user = one_user, user_ads = user_ads)
        else:
            return redirect(url_for('/login/'))
    else:
        return redirect(url_for('/login/'))
            

@app.route("/ad/<id>")
def ad(id):
    user_info = read_user_info()
    for user in user_info:
        if "user" in session == user[0]:
            ads = ad_read()
            for ad in ads:
                if int(id) == ad[0]:
                    connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
                    conn = psycopg2.connect(connection)
                    cursor = conn.cursor()
                    cursor.execute(f""" SELECT image_path FROM images WHERE ad_id = {id} """)
                    images = cursor.fetchall()
                    image_paths = [image[0] for image in images]
                    cursor.close()
                    conn.close()
                    return render_template("annonsen.html", ad = ad, image_paths = image_paths)
            else:
                pass
    else:
        return redirect(url_for("/"))
    
@app.route("/new/")
def create_ad():
    if g.user:
        user = session['user']
        user_info = read_user_info()
        for one_user in user_info:
            if user == one_user[0]:
                return render_template("ad_creation.html", one_user = one_user)
        else:
            return redirect(url_for('/login/'))
    else:
        return redirect(url_for('/login/'))
    
@app.route("/save/", methods = ['POST', 'GET'])
def save():
    if request.method == 'POST':
        title = getattr(request.form, "Title")
        description = getattr(request.form, "Description")
        price = getattr(request.form, "Price")
        type = getattr(request.form, "Typ")
        username = getattr(request.form, "Username")
        images = request.files.getlist('images')
        if title == "":
            return render_template("ad_creation.html", description = description, price = price, type = type, username = username)
        elif description == "":
            return render_template("ad_creation.html", title = title, price = price, type = type, username = username)
        elif price == "":
            return render_template("ad_creation.html", title = title, description = description, type = type, username = username)
        elif type == "":
            return render_template("ad_creation.html", description = description, price = price, username = username)
        else:
            image_paths = []
            for image in images:
                if image.filename.endswith('.jpg'):
                    # Save the file to a directory
                    image.save('Stickling.gg\Static' + image.filename)
                    # Append the file path to the list of image paths
                    image_paths.append('path/to/save/directory/' + image.filename)
            insert_ad(title, description, price, type, username, image_paths)
            return {'image_paths': image_paths}

    return render_template("ad_creation.html")
        
@app.route("/")
def index():
    """ads = ad_read()"""
    return render_template("new.html", ads = ads)

@app.route("/login/")
def login():
    return render_template("login.html")

@app.route("/logout/")
def logout():
    session.pop('user', None)
    return redirect(url_for("/"))

@app.route("/validation/", methods = ['POST', 'GET'])
def validation():
    if request.method == 'POST':
        session.pop('user', None)
        username = getattr(request.form, "Användarnamn")
        password = getattr(request.form, "Lösenord")
        user_info = read_user_info()
        for row in user_info:
            if username == row[1] and password == row[2]:
                session['user'] = username
                return render_template("new.html")
        else:
            if username != row[1] and password == row[2]:
                wrong_user = "Felaktigt användarnamn, vänligen ange ett giltigt sådant."
                return render_template("login.html", wrong_user = wrong_user)
            elif username == row[1] and password != row[2]:
                wrong_pass = "Lösenordet är inkorrekt, vänligen ange ett giltigt lösenord"
                return render_template("login.html", wrong_pass = wrong_pass)
            else:
                wrong_user_pass = "Både användarnamn och lösenord är felaktiga, vänligen ange ett giltigt input"
                return render_template("login.html", wrong_user_pass = wrong_user_pass)
            
    return render_template("login.html")
           
@app.route("/register/")
def register():
    return render_template("register.html")

@app.route("/register_user/",methods = ['POST', 'GET'])
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
        elif email !=row[0] and username != row[1] and password != row[2] and number != row[3]:
            try: 
                connection = psycopg2.connect(database="postgres", user="postgres", password="stickling", host='localhost', port="5432")
                cursor = connection.cursor()
                cursor.execute(f'INSERT INTO users(username, password, email, number) VALUES ({username}, {password}, {email}, {number});')
                cursor.close()
                connection.close()
                return render_template("login.html")
            except (Exception) as error:
               pass



if __name__ == "__main__":      
    app.run(host="127.0.0.1", port=8080, debug=True)