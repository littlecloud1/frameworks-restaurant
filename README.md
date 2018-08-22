Author: Lai Man Tang<br />
Github: https://github.com/littlecloud1/Simple-restaurant<br />
Date: 8-20-2018<br />

# frameworks-restaurant 


## Requirement
  1. Python 3 version < 3.7 (cgi.parse_multipart does not work on 3.7)
  2. Flask
  3. SQLAlchemy
  
  To install Flask:<br />
  pip install flask<br />
  
  To install SQLAlchemy:<br />
  pip install sqlalchemy<br />
  
## Files
Inputfile:
  - **webserver-restaurant.py**: do_POST and do_GET function for restaurant CRUD 
  - **webserver-post.py**: return whatever user input
  - **database_setup.py**: Restaurant database sqlalchemy schema 
  - **lotsofmenu.py**: Restaurant database from Udacity, I modify it to python 3 version
  
## How To run:

#### To run the restaurant server you have to import the database from udacity
  python database_setup.py<br />
  python lotsofmenu.py

#### run the server:<br />
  python webserver-restaurant.py <br />
and access localhost:5000/restaurants/1

