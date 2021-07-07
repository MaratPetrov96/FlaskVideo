from flask import Flask,render_template,redirect,url_for,send_from_directory,request,flash,Blueprint,g,session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,current_user,login_required,UserMixin,logout_user
from flask_wtf import FlaskForm
from flask_paginate import Pagination, get_page_parameter
from wtforms import StringField, SubmitField, TextAreaField,  BooleanField, PasswordField
from wtforms.validators import Required,InputRequired
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app=Flask(__name__, static_folder='static')
upload='static'
extensions={'mp4'}
app.config['UPLOAD_FOLDER']=upload
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'secret key'
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db=SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager=LoginManager(app)
login_manager.login_view = '/login'

class Img(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(200), nullable=False)
    sizes=db.Column(db.String(12), nullable=False)
    def __repr__(self):
        return self.title
class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200), nullable=False)
    password=db.Column(db.String(150), nullable=False)
    def __repr__(self):
        return str(self.id_)+' '+self.name+' '+self.password
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(100), nullable=False)
    username= db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.body}', '{self.timestamp}')"
class Video(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(200), nullable=False)
    description=db.Column(db.String(200), default='')
    user=db.Column(db.String(50), nullable=False)

db.create_all()
