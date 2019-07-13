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

def query_one_restaurant(get_id):
    res_query = session.query(Restaurant).filter(Restaurant.id==get_id).first()
    session.remove()
    return res_query
def query_menuItem_by_one_res_id(get_id):
    menu_query = session.query(MenuItem).filter(MenuItem.restaurant_id==get_id)
    session.remove()
    return menu_query
def query_menuItem_by_one_menu_id(get_id):
    menuItem_query = session.query(MenuItem).filter(MenuItem.id==get_id).one()
    session.remove()
    return menuItem_query

def add_menuItem(name, restaurant_id, description=None, price=None, course=None):
    newItem = MenuItem(name=name,\
                        restaurant_id=restaurant_id,\
                        description=description,\
                        price=price,\
                        course=course)
    session.add(newItem)
    try:
        session.commit()
        session.remove()
        return True
    except:
        session.remove()
        return False

def edit_menuItem(edit_item):
    session.add(edit_item)
    try:
        session.commit()
        session.remove()
        return True
    except:
        session.remove()
        return False
    
def delete_menuItem(delete_item):
    session.delete(delete_item)
    try:
        session.commit()
        session.remove()
        return True
    except:
        session.remove()
        return False


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant_query = query_one_restaurant(restaurant_id)
    res_menu = query_menuItem_by_one_res_id(restaurant_query.id)
    return render_template('menu.html', restaurant=restaurant_query, items=res_menu)

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new/', methods = ['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        print('Post Method')
        add_menuItem(request.form['name'], restaurant_id)
        flash('new menu item is created')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)
    #return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    res_menu = query_menuItem_by_one_menu_id(menu_id)
    if request.method == 'POST':
        print('Post Method')
        if request.form['name']:
            res_menu.name = request.form['name']
        edit_menuItem(res_menu)
        flash('item\'s name is updated')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, menu = res_menu)
        #return "edit page"

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    res_menu = query_menuItem_by_one_menu_id(menu_id)
    if request.method == 'POST':
        delete_menuItem(res_menu)
        flash('item\'s is deleted')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuitem.html', item = res_menu)
    return "page to delete a menu item. Task 3 complete!"

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant_query = query_one_restaurant(restaurant_id)
    res_menu = query_menuItem_by_one_res_id(restaurant_query.id)
    return jsonify(MenuItems=[i.serialize for i in res_menu])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuJSON(restaurant_id, menu_id):
    res_menu = query_menuItem_by_one_menu_id(menu_id)
    return jsonify(MenuItems=res_menu.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
