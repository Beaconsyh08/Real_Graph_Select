from flask import render_template, flash, redirect, url_for, request, Flask, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import Poem, User
import time
import datetime
from sqlalchemy import desc
from sqlalchemy.sql.expression import func


# app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = {'username': 'Mi'}
    global info
    time.sleep(1)
    info = Poem.query.filter_by(flag=0).order_by(func.random()).first()
    url = str(info.url).split(",")
    urls = [u[2:-2] for u in url]

    images = {'id': info.id,
              'poem': info.poem,
              'keyword': info.keyword,
              'url': urls,
              }
    if request.method == "POST":
        rec_data = request.json['data']

    return render_template('index.html', title='Home', user=user, images=images)


@app.route("/query", methods=["POST"])
def query():
    if request.method == "POST":
        print(request.json)
        rec_data = request.json['data']
        if str(rec_data) == "next":
            info.flag = request.json['flag']
            info.time_stamp = datetime.datetime.now()
            info.date = datetime.date.today()
            pass
        elif str(rec_data) == "previous":
            previous_info = Poem.query.filter_by(flag=1).order_by(desc(Poem.time_stamp)).first()
            previous_info.flag = request.json['flag']
            db.session.add(previous_info)
        else:
            info.chosen = rec_data
            # change the flag to 1: marked
            info.flag = request.json['flag']
            info.time_stamp = datetime.datetime.now()
            info.date = datetime.date.today()
            db.session.add(info)
        db.session.commit()
        return make_response("")


# @app.route("/previous", methods=["POST"])
# def previous():
#     if request.method == "POST":
#         previous_info = Poem.query.filter_by(flag=1).order_by(desc(Poem.time_stamp)).first()
#         previous_info.flag = request.json['flag']
#         db.session.add(previous_info)
#         db.session.commit()
#     return make_response("")

@app.route("/review")
def review():
    global review_info
    review_info = Poem.query.filter_by(flag=1).first()
    images = {'id': review_info.id,
              'poem': review_info.poem,
              'keyword': review_info.keyword,
              'chosen': review_info.chosen,
              }
    return render_template('review.html', title='Review', images=images)


@app.route("/review_query", methods=['POST'])
def review_query():
    if request.method == "POST":
        print(request.json)
        rec_data = request.json['data']
        if rec_data == "deny":
            review_info.chosen = ""
        review_info.flag = request.json['flag']
        db.session.add(review_info)
        db.session.commit()
    return make_response("")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # first(), which will return the user object if it exists, or None if it does not.
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# app.run(debug=True)
