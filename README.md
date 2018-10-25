**Author**: Lai Man Tang<br /><br />
**Github**: https://github.com/littlecloud1/frameworks-restaurant<br /><br />
**Date**: 8-20-2018<br /><br />

## Project
  This project aim to provide a user interface that user can create, read, update and delete restaurants and its' menu.
  Also, user can eaily retreive data in 4 ways by using JSON.
  
  #### Security
  The user have to login to access the restricted pages and functions ie. create, edit, and delete.
  If user does not login, the web pages will redicted to public restaurants' list, public restaurants' menu list or login pages.
  
  There are some new features is ongoing:
   * Oauth : implement google & Facebook OAuth login method.


## Requirement
  * Python 3 version < 3.7
  #### Python Lib
  * Flask
  * SQLAlchemy
  * OAuth2Client
  * Request
  * Werkzeug (Facebook OAuth require SSL for redirecting, you can use self-signed certificate, please see http://flask.pocoo.org/snippets/111/)
  
## Files
Inputfile:
  - **webserver-restaurant.py**: do_POST and do_GET function for restaurant CRUD 
  - **webserver-post.py**: return whatever user input
  - **database_setup.py**: Restaurant database sqlalchemy schema 
  - **lotsofmenu.py**: Restaurant database from Udacity, I modify it to python 3 version
  
## How To run:

#### To run the restaurant server you have to import the database from udacity
``` bash 
#build sqlalchemy database setup
python database_setup.py

#import data
python lotsofmenu.py

# run the server
python webserver-restaurant.py
``` 
The website will run in port 5000: <br/>
 localhost:5000/restaurants

