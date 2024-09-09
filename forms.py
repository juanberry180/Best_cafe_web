from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField, PasswordField
from wtforms.validators import DataRequired, URL, Email, ValidationError, InputRequired
from flask_ckeditor import CKEditorField


class CafeForm(FlaskForm):
    name = StringField("Cafe name", validators=[DataRequired()])
    img_url = FileField("File", validators=[InputRequired()])
    address = StringField("Address", validators=[DataRequired()])
    seats = StringField("Enter aprox. number of seats", validators=[DataRequired()])
    coffee_price = StringField("Caffee price", validators=[DataRequired()])
    has_sockets = SelectField("Sockets available", choices=[(0, "No"), (1, "Yes")], validators=[InputRequired()])
    has_toilet= SelectField("Toilet available", choices=[(0, "No"), (1, "Yes")], validators=[InputRequired()])
    has_wifi= SelectField("Wifi available", choices=[(0, "No"), (1, "Yes")], validators=[InputRequired()])
    can_take_calls = SelectField("Can take calls", choices=[(0, "No"), (1, "Yes")], validators=[InputRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit Cafe")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In!")



