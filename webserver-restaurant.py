#!/usr/bin/env python3
'''
    Author: Lai Man Tang(Nancy)
    Email: cloudtang030@gmail.com
    Github:https://github.com/littlecloud1
'''

import os
import random, string
from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)


# JSON
@app.route('/restaurants/JSON')
def restaurantAllJSON():
    session = DBsession()
    restaurant = session.query(Restaurant).all()

    return jsonify(Restaurant=[i.serialize for i in restaurant])


@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantOneJSON(restaurant_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(
                 id=restaurant_id).one()

    return jsonify(MenuItems=restaurant.serialize)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(
                 id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(
           restaurant_id=restaurant.id).all()

    return jsonify(MenuItems=[i.serialize for i in menu])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(
                 id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(
           restaurant_id=restaurant.id, id=menu_id).one()

    return jsonify(MenuItems=menu.serialize)


# Login session
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return  render_template('login.html')
    

# routing for restaurants' functions.
@app.route('/')
@app.route('/restaurants/')
def listRestaurants():
    session = DBsession()
    restaurants = session.query(Restaurant).all()

    return render_template('restaurant.html', items=restaurants)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    session = DBsession()

    if request.method == 'POST':

        newItem = Restaurant(name=request.form['name'])
        session.add(newItem)
        session.commit()
        flash("new restaurant created!")
        return redirect(url_for('listRestaurants'))

    else:
        return render_template('newRestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(
                 id=restaurant_id).one()

    if request.method == 'POST':

        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash(str(restaurant.name) + " has been edited!")

        return redirect(url_for('listRestaurants',
                                restaurant=restaurant))

    else:
        return render_template('editRestaurant.html',
                               restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete/',
           methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    session = DBsession()
    restaurant = session.query(Restaurant).filter_by(
                 id=restaurant_id).one()

    if request.method == 'POST':

        name = restaurant.name
        session.delete(restaurant)
        session.commit()
        flash(str(name) + " has been delete!")

        return redirect(url_for('listRestaurants'))

    else:
        return render_template('deleteRestaurant.html',
                               restaurant=restaurant)


# routing for menu items' function.
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    # create a new thread for every cursor.
    session = DBsession()

    restaurant = session.query(Restaurant).filter_by(
                id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
            restaurant_id=restaurant.id).all()
    return render_template('menu.html',
                           restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    session = DBsession()

    if request.method == 'POST':
        price = request.form['price']
        if (price[0] != '$'):
            price = '$' + price

        newItem = MenuItem(name=request.form['name'],
                           price=price,
                           description=request.form['description'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")

        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))

    else:
        return render_template('newMenuItem.html',
                               restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    session = DBsession()
    menu = session.query(MenuItem).filter_by(id=menu_id,
                                             restaurant_id=restaurant_id).one()

    if request.method == 'POST':

        menu.name = request.form['name']
        menu.price = request.form['price']
        menu.description = request.form['description']
        menu.course = request.form['course']
        session.add(menu)
        session.commit()
        flash(str(menu.name) + " has been edited!")

        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))

    else:
        return render_template('editMenuItem.html',
                               restaurant_id=restaurant_id, menu=menu)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    session = DBsession()
    menu = session.query(MenuItem).filter_by(id=menu_id,
                                             restaurant_id=restaurant_id).one()

    if request.method == 'POST':

        name = menu.name
        session.delete(menu)
        session.commit()
        flash(str(name) + " has been delete!")

        return redirect(url_for('restaurantMenu',
                        restaurant_id=restaurant_id))

    else:
        return render_template('deleteMenuItem.html',
                               restaurant_id=restaurant_id, menu=menu)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True  # reload whenever code change.
    app.run(host='0.0.0.0', port=5000)
