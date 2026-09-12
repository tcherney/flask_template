"""_Server for web access to work db_

"""

from dataclasses import dataclass
import datetime
import decimal
from functools import wraps
import os
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from sqlalchemy import DateTime, Engine, asc, create_engine, desc, extract, func, select, text
from sqlalchemy.orm import Session
from forms import EditForm, LoginForm, RegisterForm, SearchForm
from tables import Shift,Base,Store, User #,OLDShift,OLDBase
from flask_login import login_required, login_user, LoginManager, current_user, logout_user
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_APP_KEY")
Bootstrap5(app)

# old_engine: Engine = create_engine("sqlite:///backup-wis-py.db", echo=True)
# OLDBase.metadata.create_all(old_engine)
DB_URL = os.environ.get("POSTGRES_URL").replace("postgres", "postgresql", 1)
#DB_URL = "sqlite:///wis-py.db"
engine: Engine = create_engine(DB_URL, echo=True)
Base.metadata.create_all(engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "home"



def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('home'))
        elif current_user.is_authenticated and current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    with Session(engine) as session:
        return session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        with Session(engine) as session:
            if form.login.data:
                user = session.execute(select(User).where(User.email == form.email.data)).scalar()
                if user and check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('search'))
                elif not user:
                    flash("That email does not exist, please try again.")
                else:
                    flash("Password incorrect. Please try again.")
    return render_template("login.html", form=form, year=datetime.datetime.now().year)

@app.route('/about', methods=["GET", "POST"])
def about():
    return render_template("about.html", year=datetime.datetime.now().year)

@app.route('/', methods=["GET", "POST"])
def home():
    if current_user.is_authenticated is False:
        return redirect(url_for('login'))
    return render_template("index.html", year=datetime.datetime.now().year)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with Session(engine) as session:
            if form.register.data:
                user = session.execute(select(User).where(User.email == form.email.data)).scalar()
                if user:
                    flash("That email already exists, please try again.")
                elif form.password.data != form.confirm_password.data:
                    flash("Passwords do not match. Please try again.")
                else:
                    new_user = User(
                        email=form.email.data,
                        password=form.password.data
                    )
                    session.add(new_user)
                    session.commit()
                    login_user(new_user)
                    return redirect(url_for('search'))
    return render_template("index.html", form=form, year=datetime.datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True)