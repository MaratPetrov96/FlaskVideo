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
class AddCommentForm(FlaskForm):
    body = StringField("Body", validators=[InputRequired()])
    submit = SubmitField("Post")
#host='127.0.0.1',debug=True,use_reloader=False
#app.add_url_rule('/static/<filename>', 'uploaded_file',build_only=True)
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)
@app.route('/login',methods=['GET', 'POST'])
def login():
    login_=request.form.get('login')
    password=request.form.get('password')
    if login_ and password:
        user=User.query.filter_by(name=login_).first()
        try:
            user.password
        except:
            return flash('Error')
        else:
            if check_password_hash(user.password,password):
                login_user(user,remember=True)
                return redirect(url_for('main_page'))
            else:
                return flash('Error')
    else:
        flash('Fill both fields')
        return render_template('Login.html',title='Sign in',current_user=current_user) 
@app.route('/sign',methods=['GET', 'POST'])
def sign():
    sign_=request.form.get('login')
    password=request.form.get('password')
    if request.method=='POST':
        if not (sign_ or password):
            flash('Please, fill all fields')
        else:
            if User.query.filter_by(name=sign_).first()==None:
                passw=generate_password_hash(password)
                user=User(name=sign_,password=passw)
                db.session.add(user)
                db.session.commit()
                return redirect('/main/')
                #login_user(User.query.filter_by(name=sign_).first())
            else:
                flash('User already exists')
    return render_template('Sign.html',current_user=current_user)
@app.route('/download/downloading',methods=['GET', 'POST'])
@app.route('/downloading',methods=['GET', 'POST'])
@login_required
def load():
    if request.method=='POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and (file.filename.split('.')[-1] in extensions):
            filename = secure_filename(file.filename)
            user=User.query.filter_by(id=current_user.id).first()
            path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            file.save(path)
            html=secure_filename('.'.join(file.filename.split('.')[:-1]).replace(' ','_'))
            new=Video(title=html,description=request.form['description'],user=user.name)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('video',video_name=html))
@app.route('/download')
@login_required
def uploaded_file():
    return render_template('Download.html')
@app.route('/')
@app.route('/main/')
def main_page():
    return render_template('Main.html',current_user=current_user,videos=Video.query.paginate(1,7,False))
@app.route('/<int:page>')
def redirect_page(page):
    return redirect(url_for('page',page=page))
@app.route('/main/<int:page>')
def page(page):
    if page in (None,1):
        v=Video.query.paginate(1,7,False)
        return redirect(url_for('main_page'))
    v=Video.query.paginate(page,7,False)
    return render_template('Main.html',current_user=current_user,videos=v)
@app.route('/video/<string:video_name>/comment',methods=['post'])
@login_required
def comment(video_name):
    text=request.form['comment']
    user=User.query.filter_by(id=current_user.id).first()
    current_video=Video.query.filter_by(title=video_name).first()
    form = AddCommentForm()
    if text!='':
        data=Comment(body=text,username=user.name,video_id=current_video.id)
        db.session.add(data)
        db.session.commit()
    return redirect(url_for('video',video_name=video_name))
@app.route('/video/<string:video_name>')
def video(video_name):
    try:
        current_video=Video.query.filter_by(title=video_name).first()
        comments=Comment.query.filter_by(video_id=current_video.id).all()
        return render_template('Base.html',comments=comments,video=current_video)
    except:
        return redirect('main_page')
@app.route('/image')
def image():
    return render_template('Image.html',imgs=Img.query.all())
@app.route('/download_image',methods=['GET', 'POST'])
@login_required
def downloading_image():
    if request.method=='POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('main_page'))
        if file and (file.filename.split('.')[-1] in ('jpg','png')):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            sizes=str(Image.open(os.path.join(app.config['UPLOAD_FOLDER'],filename)).size)
            data=Img(title=filename,sizes=sizes)
            try:
                db.session.add(data)
                db.session.commit()
                return redirect(url_for('image'))
            except:
                return 'Ошибка'
    return render_template('Image.html',imgs=Img.query.all())
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))
if __name__=='__main__':
    app.run(debug=True)
