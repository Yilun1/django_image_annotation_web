the js code of the online annotation tool is all in filemanager/templates/canvas_modify_multifiles.html
the annotation tool can't be used by only opening the html file
it can only be used after building and running the website


install node.js
python3.6+

**install the following dependencies for the website:**

Django
djangorestframework
django-webpack-loader
django-cors-headers

**dependencies of the EAST detection algorithm:**

opencv（use pip install opencv-python） pytorch numpy pillow

**go to the folder of the project, run the following command**

npm install
npm run build
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
run the website at localhost: http://127.0.0.1:8000

**deploy it on a server**

change the "DEBUG" and "ALLOWED HOSTS" in the settings.py
change the axios default url in main.js
change all the "127.0.0.1:8000" to server url in the canvas_modify_multifiles.html 
use nginx and uwsgi to deploy it

better to use newer versions of chrome or edge
the database file is db.sqlite3
please don't mannually delete the files under media folder

