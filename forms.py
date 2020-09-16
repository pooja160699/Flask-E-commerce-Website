from wtforms import Form, StringField, PasswordField, validators, IntegerField, TextAreaField,DecimalField,SubmitField,ValidationError
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired()
    ])


class ProductForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('Stock', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_1 = FileField('Image_1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_2 = FileField('Image_2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_3 = FileField('Image_3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])

class CustomerForm(FlaskForm):
    name = StringField('Name :')
    username = StringField('Username :', validators=[DataRequired()])
    email = StringField('Email :', [validators.Email(),validators.DataRequired()])
    password =PasswordField('Password :',[validators.DataRequired(),validators.EqualTo('confirm',message='Both password must match !')])
    confirm=PasswordField('Repeat password :',[validators.DataRequired()])

    country=StringField('Country :',[validators.DataRequired()])
    state=StringField('State :',[validators.DataRequired()])
    city=StringField('City :',[validators.DataRequired()])
    contact=IntegerField('Contact :',[validators.DataRequired()])
    address=StringField('Address :',[validators.DataRequired()])
    zipcode=IntegerField('ZipCode :',[validators.DataRequired()])

    profile=FileField('Profile',validators=[FileAllowed(['jpg','png','jpeg','gif'],"Images Only please !!!")])
    submit=SubmitField('Register')
