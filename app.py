import os
import re
import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import settings as SETTINGS

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///db/sofa.db',
    DEBUG=True,
    USERNAME=SETTINGS.DB_USERNAME,
    PASSWORD=SETTINGS.DB_PASSWORD
))

db = SQLAlchemy(app)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255), unique=True)
    season_count = db.Column(db.Integer)
    description = db.Column(db.Text)

    def __init__(self, title, season_count, description):
        self.public_id = get_public_id(title)
        self.title = title
        self.season_count = season_count
        self.description = description

    def __repr__(self):
        return '<Show %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    permissions = db.Column(db.Integer)

    def __init__(self, email, username, password, first_name, last_name):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.permissions = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shows')
def shows():
    shows = Show.query.all()

    return render_template('shows.html', shows=shows)

@app.route('/shows/<show_id>')
def show_details(show_id):
    show = Show.query.filter_by(public_id=show_id).first()

    return render_template('shows-details.html', show=show)

@app.route('/shows/add', methods=['GET', 'POST'])
def show_add():
    if request.method == 'POST':
        show = Show(
            request.form['title'],
            request.form['seasons'],
            request.form['description']
        )

        db.session.add(show)
        db.session.commit()

        return redirect(url_for('shows'))

    return render_template('shows-add.html')

@app.route('/shows/<show_id>/edit', methods=['GET', 'POST'])
def show_edit(show_id):
    pass

@app.route('/shows/<show_id>/delete')
def show_delete(show_id):
    pass

@app.route('/users')
def users():
    users = User.query.all()

    return render_template('users.html', users=users)

@app.route('/users/<username>')
def user_details(username):
    user = User.query.filter_by(username=username).first()

    return render_template('user-details.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if check_password_hash(user.password, request.form['password']):
            return redirect(url_for('index'))
        else:
            return 'No dice'

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            request.form['email'],
            request.form['username'],
            request.form['password'],
            request.form['first_name'],
            request.form['last_name']
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('register.html')

def get_public_id(title):
    public_id = re.sub(r'\s', '-', title)
    public_id = re.sub(r'[^A-Za-z0-9\-]', '', public_id)
    public_id = re.sub(r'--', '-', public_id)

    return public_id.lower()

if __name__ == '__main__':
    app.run()