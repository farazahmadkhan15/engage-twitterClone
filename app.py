from flask import Flask, render_template, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, BooleanField
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import InputRequired , Length
from flask_uploads import UploadSet, IMAGES, configure_uploads
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin,login_user, login_required, current_user, logout_user
from datetime import datetime

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST']='images'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////home/farazahmadkhan/Documents/Flask_started/engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'fadfhasdbv98af34u9q2erhfbkldbdafh934823842398ureoidsjf'

login_manager = LoginManager(app)
login_manager.login_view='login'

configure_uploads(app,photos)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    image = db.Column(db.String(100))
    password = db.Column(db.String(100))
    join_date = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class RegisterForm(FlaskForm):
    name = StringField('name',
                       validators=[InputRequired('Full name is required'),
                                   Length(max=100,message='Not more than 100')])
    
    username = StringField('username',
                       validators=[InputRequired('username is required'),
                                   Length(max=100,message='Not more than 100')])
     
    password = PasswordField('Password',
                       validators=[InputRequired('Password  is required'),
                                   Length(max=30,message='Not more than 30')])
      
    image = FileField(validators=[FileAllowed(IMAGES,'Only Images Are Accepted')])
    
    
class loginForm(FlaskForm):
         
    username = StringField('username',
                       validators=[InputRequired('username is required'),
                                   Length(max=100,message='Not more than 100')])
     
    password = PasswordField('Password',
                       validators=[InputRequired('Password  is required'),
                                   Length(max=30,message='Not more than 30')])

    remember  = BooleanField("Remember Me")


@app.route('/')
def index():
    form = loginForm()

    if form.validate_on_submit():
        return "{},{}".format(form.username.data,form.password.data)
    return render_template('index.html', form=form)


@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'GET':
        redirect(url_for('index'))

    form = loginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return render_template('index.html', form=form, message="Login Failed")

        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            return redirect(url_for('profile'))

        return render_template('index.html', form=form, message="Login Failed")

    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/register', methods=["GET","POST"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)
        
        new_user = User(name=form.name.data,username=form.username.data,
                        password=generate_password_hash(form.password.data),image=image_url,
                        join_date=datetime.now())
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        return redirect(url_for('profile'))
        
        
    
    return render_template('register.html', form=form)



if __name__ == '__main__':
    manager.run()
   