import os
import re
import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for
import settings as SETTINGS

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'sofa.db'),
    DEBUG=True,
    USERNAME=SETTINGS.DB_USERNAME,
    PASSWORD=SETTINGS.DB_PASSWORD
))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row

    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shows')
def shows():
    db = get_db()  
    query = db.execute('select * from shows order by title desc')
    shows = query.fetchall()

    return render_template('shows.html', shows=shows)

@app.route('/shows/<show_id>')
def show_details(show_id):
    db = get_db()
    query = db.execute('select * from shows where show_id=?', [show_id])
    show = query.fetchone()

    return render_template('shows-details.html', show=show)

@app.route('/shows/add', methods=['GET', 'POST'])
def show_add():
    if request.method == 'POST':
        db = get_db()

        show_id = re.sub(r'\s', '-', request.form['title'])
        show_id = re.sub(r'[^A-Za-z0-9\-]', '', show_id)
        show_id = re.sub(r'--', '-', show_id)

        db.execute('insert into shows (show_id, title, seasons, description) values (?, ?, ?, ?)', [
            show_id.lower(),
            request.form['title'],
            request.form['seasons'],
            request.form['description']
        ])

        db.commit()

        return redirect(url_for('shows'))

    return render_template('shows-add.html')

@app.route('/users/<username>')
def user_details(username):
    db = get_db()

    cur = db.execute('select from users where username=?', username)

    return render_template('user-details.html', username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()

        db.execute('insert into users (username, email, password, first_name, last_name, permissions) values (?, ?, ?, ?, ?, ?)', [
            request.form['email'],
            request.form['username'],
            request.form['password'],
            request.form['first_name'],
            request.form['last_name'],
            0
        ])

        db.commit()

        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run()