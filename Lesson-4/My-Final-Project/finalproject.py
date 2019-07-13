from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem
from sqlalchemy.orm import scoped_session

OK = True
NoOK = False

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
    try:
        session.add(itemObj)
        session.commit()
        session.remove()
        return OK
    except:
        return NoOK

def queryOnefromDB(tableObj, target_id):
    res_query = session.query(tableObj).filter(tableObj.id==target_id).one()
    session.remove()
    return res_query
    
def deleteOnefromDB(itemObj):
    try:
        session.delete(itemObj)
        session.commit()
        session.remove()
        return OK
    except:
        return NoOK

def queryRestaurantMenufromDB(target_id):
    res_query = session.query(MenuItem).filter(MenuItem.restaurant_id==target_id)
    session.remove()
    return res_query


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = queryAllfromDB(Restaurant)
    return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurants/JSON')
def showRestaurantsJSON():
    restaurants = queryAllfromDB(Restaurant)
    return jsonify(Restaurants = [i.serialize for i in restaurants])

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

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['POST', 'GET'])
def deleteRestaurant(restaurant_id):
    restaurant_query = queryOnefromDB(Restaurant, restaurant_id)
    if request.method == 'POST':
        DeleteOK = deleteOnefromDB(restaurant_query)
        if DeleteOK:
            flash('%s is deleted from database' %(restaurant_query.name))
        else:
            flash('Error occurs when deleting %s' %(restaurant_query.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurant_query)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    menu_item = queryRestaurantMenufromDB(restaurant_id)
    restaurant = queryOnefromDB(Restaurant, restaurant_id)
    return render_template('menu.html', restaurant = restaurant, items = menu_item)

@app.route('/restaurant/<int:restaurant_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    menu_item = queryRestaurantMenufromDB(restaurant_id)
    return jsonify(MenuItems = [i.serialize for i in menu_item])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showMenuItemJSON(restaurant_id, menu_id):
    target_item = queryOnefromDB(MenuItem, menu_id)
    return jsonify(MenuItem = target_item.serialize)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['POST', 'GET'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],\
                            description =  request.form['description'],\
                            price = request.form['price'],\
                            course = request.form['course'],
                            restaurant_id = restaurant_id)
        addEditItemtoDB(newItem)
        flash('New menu item %s is added in database' %request.form['name'])
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html')    

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['POST', 'GET'])
def editMenuItem(restaurant_id, menu_id):
    target_item = queryOnefromDB(MenuItem, menu_id)
    if request.method == 'POST':
        old_name = target_item.name
        target_item.name = request.form['name']
        target_item.description =  request.form['description']
        target_item.price = request.form['price']
        target_item.course = request.form['course']
        addEditItemtoDB(target_item)
        flash('Menu item %s is modified in database' %old_name)
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return  render_template('editmenuitem.html', item = target_item, restaurant_id= restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['POST', 'GET'])
def deleteMenuItem(restaurant_id, menu_id):
    target_item = queryOnefromDB(MenuItem, menu_id)
    if request.method == 'POST':
        deleteOnefromDB(target_item)
        flash('Menu item %s is deleted in database' %target_item.name)
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return  render_template('deletemenuitem.html', item = target_item, restaurant_id= restaurant_id)


if __name__=='__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)