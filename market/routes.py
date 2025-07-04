import os
from market import app
from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from market import db, db_1 
from flask_login import login_user, logout_user, login_required, current_user 
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from cs50 import SQL
import sqlalchemy
import pandas as pd
from datetime import datetime
import json
import jsonpickle
from json import JSONEncoder

component = "info"
Session(app) 

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')

        
        
        
        marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=user_to_create.username)
        if not marketplace_user_rows:
            
            
            db_1.execute("INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                         username=user_to_create.username, password=form.password1.data, fname="", lname="", email=user_to_create.email_address) 
            marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=user_to_create.username)

        if marketplace_user_rows:
            session['user'] = user_to_create.username
            session['uid'] = marketplace_user_rows[0]["id"]
        

        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')

            
            marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=attempted_user.username)
            if marketplace_user_rows:
                session['user'] = attempted_user.username
                session['uid'] = marketplace_user_rows[0]["id"]
            else:
                
                
                db_1.execute("INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                             username=attempted_user.username, password=form.password.data, fname="", lname="", email=attempted_user.email_address)
                marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=attempted_user.username)
                if marketplace_user_rows:
                    session['user'] = attempted_user.username
                    session['uid'] = marketplace_user_rows[0]["id"]
            

            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    
    if 'user' in session:
        del session['user']
    if 'uid' in session:
        del session['uid']
    
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

socketio = SocketIO(app, manage_session=False)

@socketio.on('join', namespace='/chat')
def join(message):
    
    if not current_user.is_authenticated:
        return 

    room = session.get('room')
    
    chat_username = session.get('username', current_user.username)
    
    session['username'] = chat_username

    join_room(room)
    emit('status', {'msg': chat_username + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    
    if not current_user.is_authenticated:
        return 

    room = session.get('room')
    
    chat_username = session.get('username')
    emit('message', {'msg': chat_username + ' : ' + message['msg']}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    
    if 'username' in session:
        del session['username']
    if 'room' in session:
        del session['room']
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@app.route('/index', methods=['GET', 'POST'])
def index():
    
    if current_user.is_authenticated and not session.get('username'):
        
        session['username'] = current_user.username
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
@login_required 
def chat():
    
    if request.method == 'POST':
        username = request.form.get('username')
        room = request.form.get('room')

        
        if not username and current_user.is_authenticated:
            username = current_user.username

        if not username or not room:
            flash("Username and Room are required for chat!", category='danger')
            return redirect(url_for('index'))

        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session=session)
    else:
        
        if session.get('username') is not None and session.get('room') is not None:
            return render_template('chat.html', session=session)
        elif current_user.is_authenticated:
            
            return redirect(url_for('index'))
        else:
            
            flash("You need to log in to access the chat.", category='danger')
            return redirect(url_for('login_page')) 

@app.before_request
def set_marketplace_session():
    
    
    if current_user.is_authenticated and 'user' not in session:
        
        marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=current_user.username)
        if marketplace_user_rows:
            session['user'] = current_user.username
            session['uid'] = marketplace_user_rows[0]["id"]
        else:
            
            
            db_1.execute("INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                         username=current_user.username, password=current_user.password_hash, fname="", lname="", email=current_user.email_address)
            new_marketplace_user_rows = db_1.execute("SELECT id FROM users WHERE username = :username", username=current_user.username)
            if new_marketplace_user_rows:
                session['user'] = current_user.username
                session['uid'] = new_marketplace_user_rows[0]["id"]
            


@app.route("/marketplace")
@login_required 
def index_marketplace():
    shirts = db_1.execute("SELECT * FROM shirts ORDER BY team ASC")
    shirtsLen = len(shirts)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0

    
    
    
    
    if 'uid' in session: 
        shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("index_1.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    else:
        
        flash("Please log in to access your marketplace session.", "danger")
        return redirect(url_for('login_page'))


@app.route("/buy/")
@login_required
def buy():
    
    if 'uid' not in session:
        flash("Please log in to your marketplace account.", "danger")
        return redirect(url_for('login_page'))

    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    id = int(request.args.get('id'))
    goods = db_1.execute("SELECT * FROM shirts WHERE id = :id", id=id)

    if not goods:
        flash("Item not found.", "danger")
        return redirect(url_for('index_marketplace'))

    price = goods[0]["onSalePrice"] if goods[0]["onSale"] == 1 else goods[0]["price"]
    team = goods[0]["team"]
    image = goods[0]["image"]
    subTotal = qty * price

    
    db_1.execute("INSERT INTO cart (uid, id, qty, team, image, price, subTotal) VALUES (:uid, :id, :qty, :team, :image, :price, :subTotal)",
                 uid=session['uid'], id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)

    
    shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
    shopLen = len(shoppingCart)
    for item in shoppingCart:
        total += item["SUM(subTotal)"]
        totItems += item["SUM(qty)"]
    shirts = db_1.execute("SELECT * FROM shirts ORDER BY team ASC")
    shirtsLen = len(shirts)
    return render_template ("index_1.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/update/")
@login_required
def update():
    if 'uid' not in session:
        flash("Please log in to your marketplace account.", "danger")
        return redirect(url_for('login_page'))

    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    id = int(request.args.get('id'))

    
    db_1.execute("DELETE FROM cart WHERE id = :id AND uid = :uid", id=id, uid=session['uid'])

    goods = db_1.execute("SELECT * FROM shirts WHERE id = :id", id=id)
    if not goods:
        flash("Item not found.", "danger")
        return redirect(url_for('index_marketplace'))

    price = goods[0]["onSalePrice"] if goods[0]["onSale"] == 1 else goods[0]["price"]
    team = goods[0]["team"]
    image = goods[0]["image"]
    subTotal = qty * price

    
    db_1.execute("INSERT INTO cart (uid, id, qty, team, image, price, subTotal) VALUES (:uid, :id, :qty, :team, :image, :price, :subTotal)",
                 uid=session['uid'], id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal)

    shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
    shopLen = len(shoppingCart)
    for item in shoppingCart:
        total += item["SUM(subTotal)"]
        totItems += item["SUM(qty)"]
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/filter/")
@login_required 
def filter():
    
    
    shirts = [] 
    if request.args.get('continent'):
        query = request.args.get('continent')
        shirts = db_1.execute("SELECT * FROM shirts WHERE continent = :query ORDER BY team ASC", query=query )
    elif request.args.get('sale'): 
        query = request.args.get('sale')
        shirts = db_1.execute("SELECT * FROM shirts WHERE onSale = :query ORDER BY team ASC", query=query)
    elif request.args.get('id'):
        query = int(request.args.get('id'))
        shirts = db_1.execute("SELECT * FROM shirts WHERE id = :query ORDER BY team ASC", query=query)
    elif request.args.get('kind'):
        query = request.args.get('kind')
        shirts = db_1.execute("SELECT * FROM shirts WHERE kind = :query ORDER BY team ASC", query=query)
    elif request.args.get('price'):
        query = request.args.get('price') 
        shirts = db_1.execute("SELECT * FROM shirts ORDER BY onSalePrice ASC")
    else: 
        shirts = db_1.execute("SELECT * FROM shirts ORDER BY team ASC")


    shirtsLen = len(shirts)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0

    if 'uid' in session: 
        shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("index_1.html", shoppingCart=shoppingCart, shirts=shirts, shopLen=shopLen, shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ("index_1.html", shirts=shirts, shoppingCart=shoppingCart, shirtsLen=shirtsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route('/payment')
@login_required
def check():
    if 'uid' not in session:
        flash("Please log in to your marketplace account to complete your purchase.", "danger")
        return redirect(url_for('login_page'))

    order = db_1.execute("SELECT * from cart WHERE uid = :uid", uid=session['uid'])
    if not order:
        flash("Your cart is empty.", "info")
        return redirect(url_for('cart'))

    for item in order:
        db_1.execute("INSERT INTO purchases (uid, id, team, image, quantity) VALUES(:uid, :id, :team, :image, :quantity)",
                     uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"] )
    db_1.execute("DELETE from cart WHERE uid = :uid", uid=session['uid']) 

    shoppingCart = [] 
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0 
    flash("Purchase successful!", "success")
    return render_template('checkout.html')

@app.route("/remove/", methods=["GET"])
@login_required
def remove():
    if 'uid' not in session:
        flash("Please log in to your marketplace account.", "danger")
        return redirect(url_for('login_page'))

    out = int(request.args.get("id"))
    db_1.execute("DELETE from cart WHERE id=:id AND uid=:uid", id=out, uid=session['uid']) 
    totItems, total, display = 0, 0, 0
    shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    display = 1
    flash("Item removed from cart.", "info")
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )

@app.route("/history/")
@login_required
def history():
    if 'uid' not in session:
        flash("Please log in to your marketplace account to view history.", "danger")
        return redirect(url_for('login_page'))

    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    myShirts = db_1.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShirtsLen = len(myShirts)
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)

@app.route("/logout_marketplace/")
def logout_marketplace():
    
    db_1.execute("DELETE from cart WHERE uid=:uid", uid=session.get('uid')) 
    if 'user' in session:
        del session['user']
    if 'uid' in session:
        del session['uid']
    flash("You have been logged out from the marketplace!", category='info')
    
    return redirect(url_for("home_page")) 


@app.route("/cart/")
@login_required
def cart():
    if 'uid' not in session:
        flash("Please log in to your marketplace account to view your cart.", "danger")
        return redirect(url_for('login_page'))

    totItems, total, display = 0, 0, 0
    shoppingCart = db_1.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart WHERE uid = :uid GROUP BY team", uid=session['uid'])
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)