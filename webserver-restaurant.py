#!/usr/bin/env python3
'''
    Author: Lai Man Tang(Nancy)
    Email: cloudtang030@gmail.com
    Github:https://github.com/littlecloud1
'''

import os
import random, string
import httplib2, json, requests
from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)

CLIENT_ID= json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

#########################################################            
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

    
#############################################################
# Login session
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return  render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    session = DBsession()
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    #get the authorization code from post method
    code = request.data
    
    try:
        # Update the code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrad the authorization code.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # access token validation
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    
    # if error, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),
                                500)
                               

        response.headers['Content-Type'] = 'application/json'
        return response                                
    
    #verify id
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response    
    
    # check if already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("User is already connected"),
                                200)
        response.headers['Content-Type'] = 'application/json'
        return response            
    
    # Store the access token .
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    
    # Get user info
    userinfor_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfor_url, params=params)
    data = json.loads(answer.text)
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    # Check if User exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)
    login_session['user_id'] = user_id    
        
    # response html
    
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as {}".format(login_session['username']))
    return output

# Disconnect
@app.route("/gdisconnect")
def gdisconnect():
    # disconnect a user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # sending revoke token to Google OAuth
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    # if success, delete all cookies
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        
        flash("Successfully Logout.")
        return redirect(url_for('listRestaurants'))
        
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response    

   
#############################################################   
# User Account functions.
def createUser(login_session):
    session = DBsession()
    
    # Get the info from login_session
    name = login_session['username']
    email = login_session['email']
    picture = login_session['picture']
    
    #Insert into Database
    newUser = User(name=name, email=email, picture=picture)
    session.add(newUser)
    session.commit()
    
    #return user id
    user = session.query(User).filter_by(name=name, email=email).one()
    
    return user.id


def getUserInfo(user_id):
    session = DBsession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

def getUserID(email):
    session = DBsession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
    

#############################################################   
# routing for restaurants' functions.
@app.route('/')
@app.route('/restaurants/')
def listRestaurants():
    session = DBsession()
    restaurants = session.query(Restaurant).all()
    
    if 'username' not in login_session:
        return render_template('publicrestaurant.html', items=restaurants)
    
    name = login_session['username']
    return render_template('restaurant.html', items=restaurants, name=name)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
    session = DBsession()
    if request.method == 'POST':
        user_id = getUserID(login_session['email'])
        newItem = Restaurant(name=request.form['name'],user_id=user_id)
        session.add(newItem)
        session.commit()
        flash("new restaurant created!")
        return redirect(url_for('listRestaurants'))

    else:
        return render_template('newRestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
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
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
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

                               
#############################################################
# routing for menu items' function.
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    # create a new thread for every cursor.
    session = DBsession()  
    restaurant = session.query(Restaurant).filter_by(
                id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
            restaurant_id=restaurant.id).all()
    
    creator = getUserInfo(restaurant.user_id)

    if 'username' not in login_session:
        return render_template('publicmenu.html', restaurant=restaurant, items=items, creator=creator)
    
    name = login_session['username']
    return render_template('menu.html',
                           restaurant=restaurant, items=items, name=name, creator=creator)


@app.route('/restaurants/<int:restaurant_id>/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
    session = DBsession()

    if request.method == 'POST':
        price = request.form['price']
        if (price[0] != '$'):
            price = '$' + price
        user_id = getUserID(login_session['email'])
        newItem = MenuItem(name=request.form['name'],
                           price=price,
                           description=request.form['description'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id,
                           user_id=user_id)
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
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
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
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
        
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
