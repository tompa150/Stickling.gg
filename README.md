# Stickling.gg
Repository for Stickling.gg

Prerequisites:
För att kunna köra programmet behöver ni importera följande moduler.
psycopg2
Flask
bcrypt
flask_mail

Koden kommer inte att fungera utan dessa. 

Ni behöver skapa en config.py-fil som innehåller följer mallen i config.py.ex. 

mail_server='**'
mail_port= **
mai_username = '**@gmail.com'
mail_password = '**'
mail_sender = '***@gmail.com'
save_path = '**'
save_image_path = '**'

Save_path och save_image_path behöver bytas ut till era egna directorys om ni vill kunna skapa annonser. Detta gör ni genom att högerklicka på static i VScode och klickar på "Copy Path".

save_path ska sluta på stickling.gg utan  "/" och save_image_path ska sluta på "static/"

Se exempel nedan:

save_path = 'C:/Users/andym/OneDrive/Dokument/Github/Stickling.gg'
save_image_path = 'C:/Users/andym/OneDrive/Dokument/GitHub/Stickling.gg/static/

Inloggningsuppgifterna kommer att skickas i en fil på canvas till er, denna FINNS INTE PÅ GITHUB.



Steg 1:
Gå till webbserver.py filen och tryck på run-knappen längst uppe till höger.

Steg 2:
När det står att programmet kör, så gå till http://127.0.0.1:8080/ för att besöka hemsida.

Steg 3: 
När ni är färdiga med testet så kan man klicka på "soptunnan" till höger i termninalen.

