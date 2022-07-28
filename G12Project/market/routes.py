#IMPORTS
from market import app
from flask import Flask, render_template, redirect, url_for, flash, session, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from market import db
from flask_login import login_user, logout_user, login_required
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import requests
import yfinance
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


#HOME
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

#CHATBOT
@app.route('/chat_bot',methods=['GET','POST'])
@login_required
def chat_bot():
    return render_template('index_chatbot.html')

@app.route('/JARVIS',methods=['GET','POST'])
def jarvis():
    if(request.method=='POST'):
        query = input("Hello there I am JARVIS your personal stock AI. If you have any questions regarding the stock market just drop them down below. If you would like to view the performance of a stock just type 'analyze'. ")
        query = query.split()
        duration = ''  
        if "analyze" in query:
            number = int(input("Enter the number of stocks you want to analyze [e.g.) 1]: "))
            if number==1:
                stock = input("Enter the Name of the STOCK: ")
                time = input("Enter the time frame for the analysis e.g.)[ 6m, 1wk, or 7y] or type 'RANGE' if you want to specify the dates")
                if time=="RANGE":
                    start = input("Enter the opening date as YYYY-MM-DD: ").strip()
                    end = input("Enter the closing date as YYYY-MM-DD: ").strip()
                    data = yfinance.download(stock, start, end)['AdjClose']
                    data.plot()
                    plt.show()
                else:
                    stock = yfinance.Ticker(stock)
                    print(time)
                    hist = stock.history(period=time)['AdjClose']

                    hist.plot()
                    plt.show()
            else:
                stock_list = []
                for i in range(number):
                    stock = input("Enter the name of the stock: ")
                    stock_list.append(stock)

                start = input("Enter the opening date as YYYY-MM-DD: ").strip()
                end = input("Enter the ending date as YYYY-MM-DD: ").strip()
                data = yfinance.download(stock_list,  start, end)#Adj Close; Close; Open; High; Low; Open; Volume
                print(data)
                # Plot all the close prices
                ((data.pct_change()+1).cumprod()).plot(figsize=(10, 7))

                    # Show the legend
                plt.legend()

                    # Define the label for the title of the figure
                plt.title("Returns", fontsize=16)

                    # Define the labels for x-axis and y-axis
                plt.ylabel('Cumulative Returns', fontsize=14)
                plt.xlabel('Year', fontsize=14)

                    # Plot the grid lines
                plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
                plt.show()
                                
                        
        else:
            query = ("+").join(query)
            url='https://www.bing.com/news/search?q='+query 
            response = requests.get(url) 

            soup = BeautifulSoup(response.text, 'html parser') 

            headlines = soup.find('body').find_all('title') 

            for x in headlines: 

                print(x.text.strip()) 
    
    return render_template('chat_bot.html')

@app.route('/analysis', methods=['GET','POST'])
def analysis():
    if(request.method=='POST'):
        pass

#REGISTER AND LOGIN
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
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
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
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

#CHATTING ROOM :- NANOCHAT
socketio = SocketIO(app, manage_session=False)

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        username = request.form['username']
        room = request.form['room']
        #Store the data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session = session)
    else:
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))
