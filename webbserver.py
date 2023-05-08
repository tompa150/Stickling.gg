from flask import Flask, render_template, request, url_for, session, g, redirect 
import psycopg2
from datetime import timedelta
import os
import json
import bcrypt

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
    cursor.execute("SELECT username, password, email, number, salt FROM users;")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def read_user_specific(user):
    """Här läses alla användaruppgifter in från databasen"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f"SELECT username, password, email, number, salt FROM users WHERE username = '{user}';")
    user_list = cursor.fetchall()
    user = user_list[0]
    cursor.close()
    conn.close()
    return user

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

def liked_ads(username):
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    cursor.execute(f""" SELECT ads.username, ads.ad_id, ads.title, ads.description, image_pointer.image_path, ads.status FROM ads LEFT JOIN (SELECT ad_id, MIN(image_path) AS image_path FROM image_pointer GROUP BY ad_id) AS image_pointer ON ads.ad_id = image_pointer.ad_id JOIN liked_ads on ads.ad_id = liked_ads.liked_ad WHERE liked_ads.user_liking_ad = '{username}' AND ads.status = 'active' ORDER BY liked_ads.timestamp_col DESC; """)
    ads = cursor.fetchall()
    cursor.close()
    conn.close()
    return ads
    
def image_ad_read_index():
    """Här läses alla annonser från databasen in tillsammans med sökvägen till 1 bild per annons, där status = active """
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    """" Den här raden läser in alla annonsers id, titlar, beskrivningar och alla bilder som tillhör varje enskild annons.  """
    cursor.execute(f"""SELECT ads.ad_id, ads.title, ads.description, image_pointer.image_path, ads.username FROM ads LEFT JOIN (SELECT ad_id, MIN(image_path) AS image_path FROM image_pointer GROUP BY ad_id) AS image_pointer ON ads.ad_id = image_pointer.ad_id WHERE ads.status = 'active' ; """)
    results = cursor.fetchall()
    ads = {}
    for row in results:
        ad_id = row[0]
        ad_title = row[1]
        ad_description = row[2]
        image_path = row[3]
        ad_username = row[4]
        if ad_id not in ads:
            ads[ad_id] = {'title': ad_title, 'description': ad_description, 'image_path': [], 'username': ad_username}
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

def update_ad(title, ad_id, description, price, image_paths, type):
    """Denna funktionen tar emot titel, beskrivning, pris, typ, användarnamn och bildsökvägar och lägger in detta i databasen om bilerna finns, annars
    skickas användaren tillbaka till hemsidan"""
    conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
    cursor = conn.cursor()
    print(description)
    if type == "sälj":
        cursor.execute(f""" UPDATE ads SET title = '{title}', price = {price}, description = '{description}' WHERE ad_id = {ad_id}; """)
    else:
        cursor.execute(f""" UPDATE ads SET title = '{title}', description = '{description}' WHERE ad_id = {ad_id}; """)

    if image_paths != "":
            for path in image_paths:
                cursor.execute(f""" INSERT INTO image_pointer(image_path, ad_id) VALUES ('{path}', {ad_id}); """ )

    conn.commit()
    conn.close()
    return redirect('/')

def check_liked_ads(id, username):
    try:
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        cursor.execute(f""" SELECT user_liking_ad, liked_ad from liked_ads WHERE user_liking_ad = '{username}' and liked_ad = {id}; """)
        results = cursor.fetchall()
        result = results[0]
        conn.close()
        if str(result[0]) == str(username) and int(result[1]) == int(id):
            ad_is_liked = True
            return ad_is_liked
        else:
            ad_is_liked = False
            return ad_is_liked
    except:
        ad_is_liked = False
        return ad_is_liked
    
def check_liked_ads_main():
    try:
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        cursor.execute(f""" SELECT user_liking_ad, liked_ad from liked_ads; """)
        results = cursor.fetchall()
        conn.close()
        ad_is_liked = True
        return results
    except:
        ad_is_liked = False
        return ad_is_liked

@app.route("/like_ad/<id>/", methods = ['POST'])
def liking_ad(id):
    username = session['user']

    try:
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        cursor.execute(f""" INSERT into liked_ads(user_liking_ad, liked_ad) VALUES ('{username}', {id}); """)
        conn.commit()
        conn.close()
    except:
        return json.dumps({
            "success": False,
            "message": "Kunde inte spara gillningen (är den redan gillad?)"
        })    

    return json.dumps({
        "success": True,
        "message": "Gillningen är sparad i databasen"
    })

@app.route("/unlike_ad/<id>/", methods = ['POST'])
def unliking_ad(id):
    username = session['user']

    try:
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
        cursor = conn.cursor()
        cursor.execute(f""" DELETE from liked_ads WHERE user_liking_ad = '{username}' AND liked_ad = {id}; """)
        conn.commit()
        conn.close()
    except:
        return json.dumps({
            "success": False,
            "message": "Kunde inte spara borttagningen av gillning"
        })    

    return json.dumps({
        "success": True,
        "message": "Gillningen är raderad i databasen"
    })  

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

@app.route("/profile/liked_ads/")
def user_liked_ads():
    ads = image_ad_read_index()
    if 'user' not in session:
        return redirect('/')

    user_info = read_user_info()
    username = session['user']
    for one_user in user_info:
        if username == one_user[0]:
            LikedAds = liked_ads(username)
            return render_template("liked.html", LikedAds = LikedAds)

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
                ad_is_liked = check_liked_ads(id, username)
                print(ad_is_liked)
                for ad in ads:
                    if int(id) == ad[0]:
                        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432")
                        cursor = conn.cursor()
                        cursor.execute(f""" SELECT image_path FROM image_pointer WHERE ad_id = {id} """)
                        images = cursor.fetchall()
                        image_paths = [image[0] for image in images]
                        cursor.close()
                        conn.close()
                        return render_template("annonsen.html", ad = ad, image_paths = image_paths, username = username, ad_is_liked = ad_is_liked)
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
            return render_template("edit_byt.html", TheAd = TheAd, Images = Images, id = id)
        elif TheAd[5] == "efterfråga":
            return render_template("edit_efterfråga.html", TheAd = TheAd, Images = Images, id = id)
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
            type = request.form.get("Type")
            Removed_images = request.form.getlist('Deleted_images[]')
            print(Removed_images)
            image_paths = []
            for image in images:
                if image.filename.endswith(('.jpg', '.png', '.jpeg')):
                    image.filename = image.filename.replace('"', '')
                    print(image.filename)
                    image.filename = f'{ad_id}_{username}_{image.filename}'
                    if os.path.exists(os.path.join('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/', image.filename)):
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
                    else:    
                        image.save('C:/Users/Tom/Documents/GitHub/Stickling.gg/Static/' + image.filename)
                        image_paths.append(f'/static/{image.filename}')
            update_ad(title, ad_id, description, price, image_paths, type)
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
                liked_ads = check_liked_ads_main()
                print('hi')
                unmatched_values = []
                for ad in ads:
                    print(ad[4])
                    matched = False
                    for x in liked_ads:
                        if x[0] == session['user'] and x[1] == ad[0]:
                            matched = True
                            break
                    if not matched and ad[4]!= session['user']:
                        unmatched_values.append(ad[0])
                return render_template("new.html", ads = ads, session = session, liked_ads = liked_ads, unmatched_values = unmatched_values)

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
        user_info = read_user_specific(username)
        print(user_info)
        if username == user_info[0]:
            hashed_p = bcrypt.hashpw(password.encode('utf-8'), user_info[4].encode('utf-8'))
            if hashed_p == user_info[1].encode('utf-8'):
                session['user'] = username
                return redirect("/")
            else:
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
    number = request.form.get("Telefonnummer")
    user_info = read_user_info()
    print(user_info)
    for row in user_info:   
        if email == row[2] or username == row[0]:
            invalid_email = "Den angivna email/användarnamnet är redan registrerad."
            return render_template("register.html", invalid_email = invalid_email)
    else:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        print(salt)
        print(hashed)
        conn = psycopg2.connect(database="stickling_databas1", user="ai8542", password="f4ptdubn", host='pgserver.mau.se', port="5432") 
        cursor = conn.cursor()
        cursor.execute(f""" INSERT INTO users(username, password, email, number, salt) VALUES ('{username}', '{hashed.decode('utf-8')}', '{email}', {number}, '{salt.decode('utf-8')}'); """)
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
