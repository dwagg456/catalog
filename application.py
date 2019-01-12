#!/usr/bin/env python2.7

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from flask import session as login_session
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import string
import json
import requests

app = Flask(__name__)

# Google client_id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Project"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        return redirect(url_for('display_catalog'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
    return redirect(url_for('display_catalog'))


# JSON APIs to view item catalog
@app.route('/catalog/JSON')
def catalog_json():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(
        desc(Item.date_posted)).limit(10).all()
    return jsonify(categories=[category.serialize for category in categories],
                   items=[item.serialize for item in items])


@app.route('/catalog/<string:category_id>/items/JSON')
def category_json(category_id):
    categories = session.query(Category).all()
    items = session.query(Item).filter(
        Item.category_id == category_id).order_by(
            desc(Item.date_posted)).limit(10).all()
    return jsonify(categories=[category.serialize for category in categories],
                   items=[item.serialize for item in items])


@app.route('/catalog/<string:category_id>/items/<string:item_id>/JSON')
def item_json(category_id, item_id):
    item = session.query(Item).filter(Item.id == item_id).one()
    return jsonify(item=[item.serialize])


# Main catalog page
@app.route('/')
@app.route('/catalog/')
def display_catalog():
    categories = session.query(Category).all()
    items = session.query(Item.id, Item.title, Item.price, Item.category_id,
                          Category.name).filter(
                              Item.category_id == Category.id).order_by(
                                  desc(Item.date_posted)).limit(10).all()
    return render_template('catalog.html', categories=categories, items=items)


# Selected category route
@app.route('/catalog/<string:category_id>')
@app.route('/catalog/<string:category_id>/')
@app.route('/catalog/<string:category_id>/items/')
def display_category(category_id):
    categories = session.query(Category).all()
    selected_category = session.query(Category).filter(
        Category.id == category_id).one()
    items = session.query(Item.id, Item.title, Item.price, Item.category_id,
                          Category.name).filter(
                              Item.category_id == Category.id).filter(
                                  Item.category_id == category_id).order_by(
                                      desc(Item.date_posted)).all()
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           selected_category=selected_category)


# View item
@app.route('/catalog/<string:category_id>/items/<string:item_id>/')
def display_item(category_id, item_id):
    item = session.query(Item).filter(Item.id == item_id).one()
    return render_template('item.html', item=item)


# Add new item
@app.route('/catalog/<string:category_id>/items/addItem/',
           methods=['GET', 'POST'])
def add_item(category_id):
    if request.method == 'POST':
        item = Item(category_id=request.form['category_id'],
                    user_email=request.form['user_email'],
                    title=request.form['title'],
                    description=request.form['description'],
                    price=request.form['price'])
        session.add(item)
        session.commit()
        return redirect(url_for('display_category', category_id=category_id))
    else:
        return render_template('add_item.html', category_id=category_id)


# Delete item
@app.route('/catalog/<string:category_id>/items/<string:item_id>/deleteItem/',
           methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if ('email' not in login_session or
            login_session['email'] != item.user_email):
        return redirect(url_for('display_item',
                        category_id=category_id,
                        item_id=item_id))
    session.delete(item)
    session.commit()
    return redirect(url_for('display_category', category_id=category_id))


# Edit item
@app.route('/catalog/<string:category_id>/items/<string:item_id>/editItem/',
           methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if ('email' not in login_session or
            login_session['email'] != item.user_email):
        return redirect(url_for('display_item',
                                category_id=category_id,
                                item_id=item_id))
    if request.method == 'POST':
        if request.form['title']:
            item.name = request.form['title']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['price']:
            item.price = request.form['price']
        session.commit()
        return redirect(url_for('display_item',
                                category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('edit_item.html',
                               category_id=category_id,
                               item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
