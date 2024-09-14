from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField, PasswordField
from wtforms.validators import DataRequired, URL, Email, ValidationError, InputRequired
from flask_ckeditor import CKEditorField


class CafeForm(FlaskForm):
    cafe_name = StringField("Cafe name", validators=[DataRequired()])
    img_url = FileField("File", validators=[InputRequired()])
    city = StringField("City", validators=[DataRequired()])
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
    user_name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In!")


class CommentForm(FlaskForm):
    text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class ContactForm(FlaskForm):
    contact_email = StringField("Email", validators=[DataRequired(), Email()])
    contact_name = StringField("Name", validators=[DataRequired()])
    contact_text = CKEditorField("Contact", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")



