import os
import re
import sqlite3
from flask import Flask, g, redirect, render_template, request, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import settings as SETTINGS
from models import *

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///db/sofa.db',
    DEBUG=True,
    USERNAME=SETTINGS.DB_USERNAME,
    PASSWORD=SETTINGS.DB_PASSWORD,
    SECRET_KEY=SETTINGS.SECRET_KEY
))

db = SQLAlchemy(app)

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

@app.route('/users/<username>/settings')
def user_settings(username):
    if session.get('username') != username:
        return redirect(url_for('user_details', username=username))

    return render_template('user-settings.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if check_password_hash(user.password, request.form['password']):
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)

    return redirect(url_for('index'))

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