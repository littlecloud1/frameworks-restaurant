from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):

    #create a new thread for every cursor
    session = DBsession()

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ''
    for i in items:
        output += '{}<br/>'.format(i.name)
        output += '{}<br/>'.format(i.price)
        output += '{}<br/>'.format(i.description)
        output += '<br/>'
    return output
    
@app.route('/restaurants/<int:restaurant_id>/new/')
def newMenuItem(restaurant_id):
    
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"


if __name__ == '__main__':
    app.debug = True #reload whenever code change
    app.run(host = '0.0.0.0', port = 5000)
    