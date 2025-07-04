from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from market import app
from flask import Flask, render_template, redirect, url_for, flash, session, request
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = SocketIO(app, manage_session=False)

from market import routes