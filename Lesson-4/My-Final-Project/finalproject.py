from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
from sqlalchemy.orm import scoped_session


engine = create_engine('sqlite:///Lesson-3/MySitePractice/restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)

app = Flask(__name__)

def queryAllfromDB(tableObj):
    res_query = session.query(tableObj).all()
    session.remove()
    return res_query
def addEditItemtoDB(itemObj):
    session.add(itemObj)
    session.commit()
    session.remove()
def queryOnefromDB(tableObj, target_id):
    res_query = session.query(tableObj).filter(tableObj.id==target_id).one()
    session.remove()
    return res_query

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = queryAllfromDB(Restaurant)
    return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurant/new', methods=['POST', 'GET'])
def newRestaurant():
    if request.method == 'POST':
        name_from_form = request.form['name']
        newRes = Restaurant(name=name_from_form)
        addEditItemtoDB(newRes)
        flash('New restaurant %s item is added in database' %name_from_form)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['POST', 'GET'])
def editRestaurant(restaurant_id):
    restaurant_query = queryOnefromDB(Restaurant, restaurant_id)
    if request.method == 'POST':
        old_name = restaurant_query.name
        new_name = request.form['name']
        restaurant_query.name = new_name
        addEditItemtoDB(restaurant_query)
        flash('%s\'s name is changed to %s' %(old_name, new_name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=restaurant_query)

    

@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return "This page will be for deleting restaurant %s" % restaurant_id

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    return "This page is the menu for restaurant %s" % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
    return "This page is for adding new menu item for restaurant %s" % restaurant_id

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id, menu_id):
    return "This page is for editing menu item  %s" % menu_id

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id, menu_id):
    return "This page is for deleting menu item  %s" % menu_id

if __name__=='__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)