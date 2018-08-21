from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)

#JSON
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
    return jsonify(MenuItems = [i.serialize for i in menu])
    
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant.id, id =menu_id).one()
    return jsonify(MenuItems = [menu.serialize])


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):

    #create a new thread for every cursor
    session = DBsession()

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items= items)
    
@app.route('/restaurants/<int:restaurant_id>/new/', methods =['GET', 'POST'])
def newMenuItem(restaurant_id):
    session = DBsession()
    
    if request.method == 'POST':
        
        newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
    
    else :
        return render_template('newMenuItem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods= ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    session = DBsession()
    menu = session.query(MenuItem).filter_by(id = menu_id, restaurant_id = restaurant_id).one()
    
    if request.method == 'POST':
 
        menu.name = request.form['name']
        session.add(menu)
        session.commit()
        flash(str(menu.name) + " has been edited!")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
    
    else :
        return render_template('editMenuItem.html', restaurant_id = restaurant_id, menu = menu)
        
# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    session = DBsession()
    menu = session.query(MenuItem).filter_by(id = menu_id, restaurant_id = restaurant_id).one()
    
    if request.method == 'POST':
        
        name = menu.name
        session.delete(menu)
        session.commit()
        flash(str(name) + " has been delete!")
        return redirect(url_for('restaurantMenu',restaurant_id = restaurant_id))
    
    else :
        return render_template('deleteMenuItem.html', restaurant_id = restaurant_id, menu = menu)
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True #reload whenever code change
    app.run(host = '0.0.0.0', port = 5000)
    