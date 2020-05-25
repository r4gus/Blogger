# Blogger
Blog written in Python with flask

## Guide to deploy the app on heroku

### Deployment
The following third party services are required for the app to work properly
1. Heroku Postger (Database Resource on Heroku)
2. Cloudinary (Image Storage | you need to create an images folder)

After connecting the github repository to heroku, the following steps are neccessary for the app to work:

#### Exporting the required Environment Variables (Herokku -> App -> settings)
* CLOUDINARY_URL = <API environment variable>
* DATABASE_URL = <url of the postgres server>
* FLASK_APP = main.py
* FLASK_CONFIG = heroku
* POSTS_PER_PAGE = <default is 9)
* SECRET_KEY = <should be long and secret>
* SWEET_EMAIL = <email for the admin account>
* SWEET_PW = <pw for the admin account>

#### Setting up migration
On a local machine carry out the following command:
```
(venv)$ flask db init
(venv)$ flask db commit -m "initial commit"
```
and push the project, together with the __migrations__ folder on github.

#### Create Tables
The __main.deploy()__ function can be used to deploy the app. It uses the update() function to update the database
based on the migration file.

| Changes to the database must be commited localy with __db commit__ and then pushed on github

The database tables must be created before the deploy script can be executed. In order to do so open a shell on heroku and type
```
heroku run flask shell
>>> db.create_all()
```
After that the deploy function can be executed:
```
flask run flask deploy
```

The deploy function also creates an admin account based on SWEET_EMAIL and SWEET_PW.

After that the app should be fully functional.
