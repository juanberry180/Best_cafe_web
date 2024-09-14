from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CafeForm, RegisterForm, LoginForm, CommentForm, ContactForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from contact_message import MessageSend
from sqlalchemy.testing.pickleable import User
import os
import datetime
from typing import List
from flask_gravatar import Gravatar
from functools import wraps



app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
app.config['UPLOAD_FOLDER'] = 'static/assets/cafe_pics'
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app,
                    size=20,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafes(db.Model):
    __tablename__ = "cafe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[int] = mapped_column(Integer, nullable=True)
    has_toilet: Mapped[int] = mapped_column(Integer, nullable=True)
    has_wifi: Mapped[int] = mapped_column(Integer, nullable=True)
    can_take_calls: Mapped[int] = mapped_column(Integer, nullable=True)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    input_date: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    comments: Mapped[List["Comment"]] = relationship(back_populates="cafe_name")


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    user_name: Mapped[str] = mapped_column(String(250), nullable=False)
    comments: Mapped[List["Comment"]] = relationship(back_populates="user_name")
    cafes: Mapped[List["Cafes"]] = relationship()


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user_name = relationship("User", back_populates="comments")
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafe.id"))
    cafe_name = relationship("Cafes", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)



with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user._get_current_object().id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function

@app.route('/')
def home():
    all_cafes = db.session.execute(db.select(Cafes).order_by(Cafes.id)).scalars().all()
    return render_template("index.html", all_cafes=all_cafes[0:6])

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data.lower()
        user_name = register_form.user_name.data.lower()
        hashed_password = generate_password_hash(password=register_form.password.data, method='pbkdf2:sha256', salt_length=8)
        if db.session.query(User).filter_by(email=email).scalar():
            flash("User already exists new")
            return redirect(url_for('login'))

        else:
            new_user = User(email=email, password=hashed_password, user_name=user_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=register_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data.lower()
        user = User.query.filter_by(email=email).scalar()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Invalid Username or password, please check your email and password", 'error')
        else:
            flash("User not found, please check your email and password", 'error')

    return render_template("login.html", form=login_form)


@app.route('/new-place', methods=['GET', 'POST'])
def add_new_place():
    cafe_form = CafeForm()
    if cafe_form.validate_on_submit():
        img_url = cafe_form.img_url.data
        img_url.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],secure_filename(img_url.filename)))
        path=f'/static/assets/cafe_pics/{img_url.filename}'
        new_cafe = Cafes(
            cafe_name = cafe_form.cafe_name.data,
            img_url = path,
            city=cafe_form.city.data,
            address = cafe_form.address.data,
            has_sockets = cafe_form.has_sockets.data,
            has_toilet = cafe_form.has_toilet.data,
            has_wifi = cafe_form.has_wifi.data,
            can_take_calls = cafe_form.can_take_calls.data,
            seats = cafe_form.seats.data,
            coffee_price = cafe_form.coffee_price.data,
            description = cafe_form.description.data,
            input_date = datetime.datetime.now().date(),
            user_id = current_user.id)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_place.html", form=cafe_form)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        contact_email = contact_form.contact_email.data.lower()
        contact_name = contact_form.contact_name.data.lower()
        contact_text = contact_form.contact_text.data
        try:
            messegeSend = MessageSend(contact_email,contact_text,contact_name)
            flash("Message send sucessfully", "success")
            return redirect(url_for('contact'))
        except:
            flash("Message not send sucessfully", "flash")
            return redirect(url_for('contact'))

    return render_template("contact.html", form=contact_form)




@app.route('/cafe_post/<int:cafe_id>', methods=['GET', 'POST'])
def cafe_post(cafe_id):
    cafe = db.get_or_404(Cafes, cafe_id)
    comments = Comment.query.filter_by(cafe_id=cafe_id).all()
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        new_comment = Comment(
            user_id = current_user.id,
            cafe_id = cafe_id,
            text = comment_form.text.data)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment submited sucessfully")
        return redirect(url_for('cafe_post', cafe_id=cafe_id))
    return render_template("cafe_post.html", cafe=cafe, form=comment_form, comments=comments)

@app.route('/cafes', methods=['GET', 'POST'])
def cafes():
    if current_user.is_authenticated:
        current_user_id = current_user.id
        all_cafes = db.session.execute(db.select(Cafes).order_by(Cafes.id)).scalars().all()
        return render_template("cafes.html", all_cafes=all_cafes, current_user_id = current_user.id)

    else:
        all_cafes = db.session.execute(db.select(Cafes).order_by(Cafes.id)).scalars().all()
        return render_template("cafes.html", all_cafes=all_cafes)



@app.route('/delete/<int:cafe_id>')
@admin_only
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafes, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))






if __name__ == '__main__':
    app.run(debug=True)
