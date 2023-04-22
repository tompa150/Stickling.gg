from flask import Flask, render_template, request, url_for, session, g, redirect 
import psycopg2
from datetime import timedelta
import os

app = Flask(__name__, template_folder='HTML')
app.secret_key = "stickling.gg"

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)

def new_ad_id():
    largest_id = 1
    ads = ad_read_for_new_id()
    for ad in ads:
        if ad[0] >= largest_id:
            largest_id = ad[0] + 1
    return largest_id

def connect_to_db():
    
    """Skapat en funktion som ansluter till databasen. Den här funktionen kan vi sedan kalla på i alla andra funktioner. 
    Så slipper vi skriva ut strängen varje gång, eller bara ändra på ett ställe om vi ska ändra något. """
    
    connection = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    return connection
    
def read_user_info():
    """Här läses alla användaruppgifter in från databasen"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, email, number FROM users;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def ad_read():
    """Här läses alla annonser från databasen där statusen = active """
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(""" SELECT * FROM ads WHERE ads.status = 'active'; """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def ad_read_for_new_id():
    """Här läses alla annonser från databasen där statusen = active """
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(""" SELECT * FROM ads; """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def image_ad_read_active(user):
    """Här läses alla annonser från databasen in, tillsammans med alla dess bilders sökvägar, där statusen = active """
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" SELECT ads.ad_id, ads.title, ads.description, image_pointer.image_path, ads.status FROM ads LEFT JOIN (SELECT ad_id, MIN(image_path) AS image_path FROM image_pointer GROUP BY ad_id) AS image_pointer ON ads.ad_id = image_pointer.ad_id WHERE ads.username = '{user}' AND ads.status = 'active' """)
    results = cursor.fetchall()
    ads = {}
    for row in results:
        ad_id = row[0]
        ad_title = row[1]
        ad_description = row[2]
        image_path = row[3]
        status = row[4]
        if ad_id not in ads:
            ads[ad_id] = {'title': ad_title, 'description': ad_description, 'image_paths': [], 'status': status}
        ads[ad_id]['image_paths'].append(image_path)
    conn.close()
    return results

def id_ad(id):
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" SELECT * FROM ads WHERE ads.ad_id = {id}; """)
    ads = cursor.fetchall()
    ad = ads[0]
    cursor.close()
    conn.close()
    return ad
    

def image_ad_read_inactive(user):
    """Här läses alla annonser in från databasen, tillsammans med 1 bild per annons, där status = inactive"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" SELECT ads.ad_id, ads.title, ads.description, image_pointer.image_path, ads.status FROM ads LEFT JOIN (SELECT ad_id, MIN(image_path) AS image_path FROM image_pointer GROUP BY ad_id) AS image_pointer ON ads.ad_id = image_pointer.ad_id WHERE ads.username = '{user}' AND ads.status = 'inactive' """)
    results = cursor.fetchall()
    ads = {}
    for row in results:
        ad_id = row[0]
        ad_title = row[1]
        ad_description = row[2]
        image_path = row[3]
        status = row[4]
        if ad_id not in ads:
            ads[ad_id] = {'title': ad_title, 'description': ad_description, 'image_paths': [], 'status': status}
        ads[ad_id]['image_paths'].append(image_path)
    conn.close()
    return results
    
def image_ad_read_index():
    """Här läses alla annonser från databasen in tillsammans med sökvägen till 1 bild per annons, där status = active """
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    """" Den här raden läser in alla annonsers id, titlar, beskrivningar och alla bilder som tillhör varje enskild annons.  """
    cursor.execute(f"""SELECT ads.ad_id, ads.title, ads.description, image_pointer.image_path FROM ads LEFT JOIN (SELECT ad_id, MIN(image_path) AS image_path FROM image_pointer GROUP BY ad_id) AS image_pointer ON ads.ad_id = image_pointer.ad_id WHERE ads.status = 'active' ; """)
    results = cursor.fetchall()
    ads = {}
    for row in results:
        ad_id = row[0]
        ad_title = row[1]
        ad_description = row[2]
        image_path = row[3]
        if ad_id not in ads:
            ads[ad_id] = {'title': ad_title, 'description': ad_description, 'image_path': []}
        ads[ad_id]['image_path'].append(image_path)
    conn.close()
    return results

def ReadAdImages(id):
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" SELECT image_path from image_pointer WHERE image_pointer.ad_id = {id}; """)
    results = cursor.fetchall()
    conn.close()
    images = [row[0] for row in results]
    return images

def insert_ad(title, description, price, type, username, image_paths):
    """Denna funktionen tar emot titel, beskrivning, pris, typ, användarnamn och bildsökvägar och lägger in detta i databasen om bilerna finns, annars
    skickas användaren tillbaka till hemsidan"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    ad_id = new_ad_id()
    if type == "sälj":
        cursor.execute(f""" INSERT into ads(ad_id, username, title, price, description, ad_type, status) VALUES ({ad_id}, '{username}', '{title}', {price}, '{description}', '{type}', 'active'); """)
        for path in image_paths:
            cursor.execute(f""" INSERT INTO image_pointer(image_path, ad_id) VALUES ('{path}', {ad_id}); """ )
    elif type == "byt":
        cursor.execute(f""" INSERT into ads(ad_id, username, title, description, ad_type, status) VALUES ({ad_id}, '{username}', '{title}', '{description}', '{type}', 'active'); """)
        for path in image_paths:
            cursor.execute(f""" INSERT INTO image_pointer(image_path, ad_id) VALUES ('{path}', {ad_id}) """ )
    elif type == "efterfråga":
        cursor.execute(f""" INSERT into ads(ad_id, username, title, description, ad_type, status) VALUES ({ad_id}, '{username}', '{title}', '{description}', '{type}', 'active'); """)
        for path in image_paths:
            cursor.execute(f""" INSERT INTO image_pointer(image_path, ad_id) VALUES ('{path}', {ad_id}) """ )
    conn.commit()
    conn.close()
    return redirect('/')

def delete_images(Removed_images):
    if Removed_images != "":
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        for path in Removed_images:
            cursor.execute(f""" DELETE from image_pointer WHERE image_pointer.image_path = '{path}'; """ )
            os.remove(f'C:/Users/Tom/Documents/GitHub/Stickling.gg{path}')
        conn.commit()
        conn.close()
        return
    else:
        return

def update_ad(title, ad_id, description, price, image_paths):
    """Denna funktionen tar emot titel, beskrivning, pris, typ, användarnamn och bildsökvägar och lägger in detta i databasen om bilerna finns, annars
    skickas användaren tillbaka till hemsidan"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" UPDATE ads SET title = '{title}', price = {price}, description = '{description}' WHERE ad_id = {ad_id}; """)
    if image_paths != "":
        for path in image_paths:
            cursor.execute(f""" INSERT INTO image_pointer(image_path, ad_id) VALUES ('{path}', {ad_id}); """ )
    conn.commit()
    conn.close()
    return redirect('/')

@app.route("/profile/")
def profile():
    """Här för denna URI så returneras profile.html tillsammans med alla aktiva och inaktiva annonser som en 
    specifik användare har """
    if 'user' not in session:
        return redirect('/')

    user_info = read_user_info()
    user = session['user']
    for one_user in user_info:
        if user == one_user[0]:
            active_ads = image_ad_read_active(user)
            inactive_ads = image_ad_read_inactive(user)
            return render_template("profile.html", active_ads = active_ads, inactive_ads = inactive_ads)

    return redirect(url_for('login'))

@app.route("/ad/<id>/")
def ad(id):
    """Här tar funktionen emot ett id från URI och letar sedan i databasen efter en annons med ett matchande id, finns det
    så returneras annonsen.html tillsammans med titeln, priset och beskrivningen och bilderna för annonsen."""
    if 'user' not in session:
        return redirect('/')
    else:
        user_info = read_user_info()
        for user in user_info:
            if session['user'] == user[0]:
                username = session['user']
                ads = ad_read()
                for ad in ads:
                    if int(id) == ad[0]:
                        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
                        cursor = conn.cursor()
                        cursor.execute(f""" SELECT image_path FROM image_pointer WHERE ad_id = {id} """)
                        images = cursor.fetchall()
                        image_paths = [image[0] for image in images]
                        cursor.close()
                        conn.close()
                        return render_template("annonsen.html", ad = ad, image_paths = image_paths, username = username)
                else:
                    return redirect('/')
        
'''
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
'''
    
@app.route("/save/", methods = ['POST', 'GET'])
def save():
    """I denna funktionen tas titel, beskrivning, typ, pris, användarnamn, bildsökvägar emot från ett formulär.
        om någon av dessa är tomma får användaren göra om annonsen den vill skapa. om ingen av dessa är tomma läggs dessa in i databasen."""
    if request.method == 'POST':
        title = request.form.get("Title")
        description = request.form.get("Description")
        price = request.form.get("Price")
        type = request.form.get("Type")
        username = request.form.get("Username")
        images = request.files.getlist("images")
        if title == "":
            return render_template("ad_creation.html", description = description, price = price, type = type, username = username)
        elif description == "":
            return render_template("ad_creation.html", title = title, price = price, type = type, username = username)
        elif type == "":
            return render_template("ad_creation.html", description = description, price = price, username = username)
        else:
            image_paths = []
            for image in images:
                if image.filename.endswith(('.jpg', '.png', '.jpeg')):
                    image.filename = f'{title}_{username}_{image.filename}'
                    if os.path.exists(os.path.join('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/', image.filename)):
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
                    else:    
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
            insert_ad(title, description, price, type, username, image_paths)
            return redirect("/")

    return render_template("ad_creation.html")

@app.route("/edit/<id>/")
def edit_article(id):
    if 'user' not in session:
        return redirect('/')
    else:
        TheAd = id_ad(id)
        Images = ReadAdImages(id)
        print(Images)
        if TheAd[5] == 'sälj':
            return render_template("edit_sälj.html", TheAd = TheAd, Images = Images, id = id)
        elif TheAd[5] == "byt":
            return render_template("edit_byt.html", TheAd = TheAd, Images = Images)
        elif TheAd[5] == "efterfråga":
            return render_template("edit_efterfråga.html", TheAd = TheAd, Images = Images)
        else:
            return redirect(f'/ad/{id}/')
 
@app.route("/update/", methods = ['POST', 'GET'])
def update():
    if 'user' not in session:
        return redirect('/')
    else:
        if request.method == 'POST':
            ad_id = request.form.get("Ad_id")
            title = request.form.get("Title")
            description = request.form.get("Description")
            price = request.form.get("Price")
            username = request.form.get("Username")
            images = request.files.getlist("images")
            Removed_images = request.form.getlist('Deleted_images[]')
            print(Removed_images)
            image_paths = []
            for image in images:
                if image.filename.endswith(('.jpg', '.png', '.jpeg')):
                    image.filename = f'{title}_{username}_{image.filename}'
                    if os.path.exists(os.path.join('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/', image.filename)):
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
                    else:    
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
            update_ad(title, ad_id, description, price, image_paths)
            delete_images(Removed_images)
            return redirect("/")
            
@app.route("/remove/", methods = ['POST', 'GET'])
def remove():
    if request.method == 'POST':
        AdToDelete = request.form.get("ad_id")

        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        cursor.execute(f""" UPDATE ads SET status = 'inactive' WHERE ad_id = {AdToDelete}; """)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    else:
        pass
   
@app.route("/")
def index():
    """För denna URI returneras new.html tillsammans med alla annonser och användarens session."""
    ads = image_ad_read_index()
    if 'user' not in session:
        return render_template("new.html", ads = ads)
    else:
        user_info = read_user_info()
        for user in user_info:
            if session['user'] == user[0]:
                return render_template("new.html", ads = ads, session = session)

@app.route("/login/")
def login():
    """Här returneras login.html"""
    return render_template("login.html")

@app.route("/new/choose_ad/")
def choose_ad():
    """Här returneras choose_ad.html"""
    if 'user' not in session:
        return redirect("/")
    else:
        return render_template("choose_ad.html")

@app.route("/new/1/")
def new_1():
    """Här returneras ad_sälj.html"""
    if 'user' not in session:
        return redirect("/")
    else:
        user = session['user']
        return render_template("Create_Sell.html", user = user)
    
@app.route("/new/2/")
def new_2():
    """Här returneras ad_byt.html"""
    if 'user' not in session:
        return redirect("/")
    else:
        user = session['user']
        return render_template("ad_byt.html", user = user)
    
@app.route("/new/3/")
def new_3():
    """Här returneras ad_efterfråga.html"""
    if 'user' not in session:
        return redirect("/")
    else:
        user = session['user']
        return render_template("ad_efterfråga.html", user = user)

@app.route("/logout/")
def logout():
    """Här loggas användaren ut och skickar användaren till hemskärmen """
    session.pop('user', None)
    return redirect("/")

@app.route("/validation/", methods = ['POST', 'GET'])
def validation():
    """Här loggas användaren ut om den är inloggad, den tar sen emot användarnamn och lösen ord och sparar användaren i en session"""
    if request.method == 'POST':
        session.pop('user', None)
        username = request.form.get("Username")
        password = request.form.get("Password")
        user_info = read_user_info()
        for row in user_info:
            if username == row[0] and password == row[1]:
                session['user'] = username
                return redirect("/")
        else:
            if username != row[0] and password == row[1]:
                wrong_user = "Felaktigt användarnamn, vänligen ange ett giltigt sådant."
                return render_template("login.html", wrong_user = wrong_user)
            elif username == row[0] and password != row[1]:
                wrong_pass = "Lösenordet är inkorrekt, vänligen ange ett giltigt lösenord"
                return render_template("login.html", wrong_pass = wrong_pass)
            else:
                wrong_user_pass = "Både användarnamn och lösenord är felaktiga, vänligen ange ett giltigt input"
                return render_template("login.html", wrong_user_pass = wrong_user_pass)
            
    return render_template("login.html")
           
@app.route("/register/")
def register():
    """Här returneras register.html"""
    return render_template("register.html")

@app.route("/register/new/", methods = ['POST', 'GET'])
def register_user():
    """Här tas användaruppgifter emot från ett formulär, sedan läses alla befintliga användare in. Om inget av dom krocka med befintliga användaruppgifter
    läggs användarens uppgifter in i databasen."""
    email = request.form.get("Email")
    username = request.form.get("Användarnamn")
    password = request.form.get("Lösenord")
    conf_password = request.form.get("Bekräfta_lösenord")
    number = request.form.get("Telefonnummer")
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
    else:
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432") 
        cursor = conn.cursor()
        cursor.execute(f""" INSERT INTO users(username, password, email, number) VALUES ('{username}', '{password}', '{email}', {number}); """)
        conn.commit()
        conn.close()
        return render_template("login.html")
            
'''
@app.route('/register/forgot_password/', methods = ['POST', 'GET'])
def ForgPassword():
'''

"""@app.route("/about/")
    def about():_
    return render_template """


if __name__ == "__main__":      
    app.run(host="127.0.0.1", port=8080, debug=True) #Här körs programmet
