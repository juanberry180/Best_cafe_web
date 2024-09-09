from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CafeForm, RegisterForm, LoginForm
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'static/assets/cafe_pics'
Bootstrap5(app)

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafes(db.Model):
    __tablename__ = "cafe"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[int] = mapped_column(Integer, nullable=True)
    has_toilet: Mapped[int] = mapped_column(Integer, nullable=True)
    has_wifi: Mapped[int] = mapped_column(Integer, nullable=True)
    can_take_calls: Mapped[int] = mapped_column(Integer, nullable=True)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    input_date: Mapped[str] = mapped_column(String(250), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_cafes = db.session.execute(db.select(Cafes).order_by(Cafes.id)).scalars().all()
    return render_template("index.html", all_cafes=all_cafes[0:len(all_cafes)])

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data.lower()
        name = register_form.name.data.lower()
        hashed_password = generate_password_hash(password=register_form.password.data, method='pbkdf2:sha256', salt_length=8)
        if db.session.query(User).filter_by(email=email).scalar():
            return redirect(url_for('login'))
        else:
            new_user = User(email=email, password=hashed_password, name=name)
            db.session.add(new_user)
            db.session.commit()
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
                return redirect(url_for('home'))
            else:
                flash("Invalid Username or password, please check your email and password", 'error')
        else:
            flash("User not found, please check your email and password")
    return render_template("login.html", form=login_form)


@app.route('/new-place', methods=['GET', 'POST'])
def add_new_place():
    cafe_form = CafeForm()
    if cafe_form.validate_on_submit():
        img_url = cafe_form.img_url.data
        img_url.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],secure_filename(img_url.filename)))
        path=f'/static/assets/cafe_pics/{img_url.filename}'
        new_cafe = Cafes(
            name = cafe_form.name.data,
            img_url = path,
            address = cafe_form.address.data,
            has_sockets = cafe_form.has_sockets.data,
            has_toilet = cafe_form.has_toilet.data,
            has_wifi = cafe_form.has_wifi.data,
            can_take_calls = cafe_form.can_take_calls.data,
            seats = cafe_form.seats.data,
            coffee_price = cafe_form.coffee_price.data,
            description = cafe_form.description.data,
            input_date = datetime.datetime.now().date())
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_place.html", form=cafe_form)

@app.route('/cafe_post/<int:cafe_id>', methods=['GET', 'POST'])
def cafe_post(cafe_id):
    cafe = db.get_or_404(Cafes, cafe_id)
    return render_template("cafe_post.html", cafe=cafe)


@app.route('/delete/<int:cafe_id>')
def delete_cafe(cafe_id):
    cafe_to_delete = db.get_or_404(Cafes, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
