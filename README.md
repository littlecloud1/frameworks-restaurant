**Author**: Lai Man Tang<br /><br />
**Github**: https://github.com/littlecloud1/frameworks-restaurant<br /><br />
**Date**: 8-20-2018<br /><br />

# frameworks-restaurant 


## Requirement
  1. Python 3 version < 3.7 (cgi.parse_multipart does not work on 3.7)
  2. Flask
  3. SQLAlchemy
  
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

