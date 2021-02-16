from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import InputRequired , Length
from flask_uploads import UploadSet, IMAGES, configure_uploads
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST']='images'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////home/farazahmadkhan/Documents/Flask_started/engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'fadfhasdbv98af34u9q2erhfbkldbdafh934823842398ureoidsjf'


configure_uploads(app,photos)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    image = db.Column(db.String(100))
    password = db.Column(db.String(100))
    
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
    
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

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
                        password=generate_password_hash(form.password.data),image=image_url)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('profile'))
        
        
    
    return render_template('register.html', form=form)



if __name__ == '__main__':
    manager.run()
   