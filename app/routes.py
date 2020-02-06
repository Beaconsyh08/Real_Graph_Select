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
"""
flag = 0: ready to mark
flag = 1: marked
flag = 2: no satisfied graph
flag = 3: confirmed
flag = 4: denied
"""


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user_info = {'username': str(current_user)[6:-1]}
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

    global marked_img_count
    marked_img_count = Poem.query.filter_by(flag=1).count()
    no_sat_img_count = Poem.query.filter_by(flag=2).count()

    choose_numbers = {
        'marked': marked_img_count,
        'viewed': marked_img_count + no_sat_img_count
    }
    return render_template('index.html', title='Home', user=user_info, images=images, numbers=choose_numbers)


@app.route("/query", methods=["POST"])
def query():
    if request.method == "POST":
        print(request.json)
        rec_data = request.json['data']
        if str(rec_data) == "next":
            info.flag = request.json['flag']
            info.time_stamp = datetime.datetime.now()
            info.date = datetime.date.today()
            info.marked_by = str(current_user)[6:-1]
            db.session.add(info)

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
            info.marked_by = str(current_user)[6:-1]
            db.session.add(info)
        db.session.commit()
        return make_response("")


@app.route("/review")
@login_required
def review():
    global review_info
    time.sleep(1)
    confirmed_img_count = Poem.query.filter_by(flag=3).count()
    denied_img_count = Poem.query.filter_by(flag=4).count()

    if marked_img_count > 0:
        review_info = Poem.query.filter_by(flag=1).first()
        images = {'id': review_info.id,
                  'poem': review_info.poem,
                  'keyword': review_info.keyword,
                  'chosen': review_info.chosen,
                  }
    else:
        review_info = None
        images = {'id': "Sorry",
                  'poem': "No poem has been marked",
                  'keyword': "!",
                  'chosen': "https://images.unsplash.com/photo-1525847664954-bcd1e64c6ad8?ixlib=rb-1.2.1&amp;ixid=eyJhcHBfaWQiOjEyMDd9&amp;auto=format&amp;fit=crop&amp;w=1000&amp;q=80",
                  }

    review_numbers = {
        'marked': marked_img_count,
        'confirmed': confirmed_img_count,
        'denied': denied_img_count
    }
    return render_template('review.html', title='Review', images=images, numbers=review_numbers)


@app.route("/review_query", methods=['POST'])
def review_query():
    if review is not None:
        if request.method == "POST":
            print(request.json)
            rec_data = request.json['data']
            if rec_data == "confirm":
                review_info.confirmed_by = str(current_user)[6:-1]
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
