import os
import re
import sqlite3
from collections import defaultdict
from enum import Enum
from flask import abort, Flask, g, redirect, render_template, request, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import settings as SETTINGS

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///db/sofa.db',
    DEBUG=True,
    USERNAME=SETTINGS.DB_USERNAME,
    PASSWORD=SETTINGS.DB_PASSWORD,
    SECRET_KEY=SETTINGS.SECRET_KEY
))

class Status(Enum):
    NONE = 0
    WAITING = 1
    WATCHING = 2
    PAUSED = 4
    STOPPED = 8

db = SQLAlchemy(app)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255), unique=True)
    season_count = db.Column(db.Integer)
    description = db.Column(db.Text)
    episodes = db.relationship('Episode', backref='show', cascade='all, delete-orphan', lazy='dynamic')

    def __init__(self, title, season_count, description):
        self.public_id = get_public_id(title)
        self.title = title
        self.season_count = season_count
        self.description = description

    def __repr__(self):
        return '<Show %r>' % self.title

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255))
    title = db.Column(db.String(255))
    season = db.Column(db.Integer)
    number = db.Column(db.Integer)
    description = db.Column(db.Text)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

    def __init__(self, title, season, number, description, show_id):
        self.public_id = get_public_id(title)
        self.title = title
        self.season = season
        self.number = number
        self.description = description
        self.show_id = show_id

    def __repr__(self):
        return '<Episode %r>' % self.title

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'))
    status = db.Column(db.Integer)

    def __init__(self, show_id, episode_id, status):
        self.show_id = show_id
        self.episode_id = episode_id
        self.status = status

    @property
    def show(self):
        return Show.query.filter_by(id=self.show_id).first()

    @property
    def episode(self):
        return Episode.query.filter_by(id=self.episode_id).first()

    def __repr__(self):
        return '<Progress %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    permissions = db.Column(db.Integer)
    watching = db.relationship('Progress', backref='progress', secondary='watching', lazy='dynamic')
    favorites = db.relationship('Show', backref='show', secondary='favorites', lazy='dynamic')

    def __init__(self, email, username, password, first_name, last_name):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.permissions = 0

    def get_watching(self):
        return [progress for progress in self.watching]

    def add_watching(self, progress):
        self.watching.append(progress)

    def get_favorites(self):
        return [show for show in self.favorites]

    def add_favorite(self, show):
        self.favorites.append(show)

    def remove_favorite(self, show):
        self.favorites.remove(show)

    def __repr__(self):
        return '<User %r>' % self.username

watching = db.Table('watching',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('progress_id', db.Integer, db.ForeignKey('progress.id'))
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('show_id', db.Integer, db.ForeignKey('show.id'))
)

def get_public_id(title):
    public_id = re.sub(r'\s', '-', title)
    public_id = re.sub(r'[^A-Za-z0-9\-]', '', public_id)
    public_id = re.sub(r'--', '-', public_id)

    return public_id.lower()

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return redirect(url_for('index'))

    search = request.form['search']
    q =  '%' + search + '%'

    results = dict(
        shows=Show.query.filter(Show.title.like(q)).all(),
        episodes=Episode.query.filter(Episode.title.like(q)).all(),
        users=User.query.filter(User.username.like(q)).all()
    )

    print results #dev

    return render_template('search-results.html', search=search, results=results)

@app.route('/shows')
def shows():
    shows = Show.query.all()

    return render_template('shows.html', shows=shows)

@app.route('/shows/<show_id>')
def show_details(show_id):
    user = User.query.filter_by(username=session.get('username')).first()
    show = Show.query.filter_by(public_id=show_id).first()
    episodes = Episode.query.filter_by(show_id=show.id).all()

    if user:
        watching = any(show.id == progress.id for progress in user.get_watching())
        favorited = any(show_id == show.public_id for show in user.get_favorites())
    else:
        watching = False
        favorited = False

    seasons = defaultdict(list)

    for episode in episodes:
        seasons[episode.season].append(episode)

    return render_template('show-details.html', show=show, seasons=seasons, watching=watching, favorited=favorited)

@app.route('/shows/<show_id>/start')
def show_start(show_id):
    if session.get('username'):
        user = User.query.filter_by(username=session.get('username')).first()
        show = Show.query.filter_by(public_id=show_id).first()
        episode = Episode.query.filter_by(season=1).filter_by(number=1).first()

        watching = any(show.id == progress.show_id for progress in user.get_watching())

        if not watching:
            progress = Progress(
                show.id,
                episode.id,
                Status.WATCHING.value
            )

            db.session.add(progress)
            user.add_watching(progress)
            db.session.commit()

    return redirect(url_for('show_details', show_id=show_id))

@app.route('/shows/<show_id>/pause')
def show_pause(show_id):
    if session.get('username'):
        user = User.query.filter_by(username=session.get('username')).first()
        show = Show.query.filter_by(public_id=show_id).first()

        watching = any(show.id == progress.show_id for progress in user.get_watching())

        if watching:
            progress = Progress.query.filter_by(show_id=show.id).first()
            progress.status = Status.PAUSED.value
            db.session.commit()

    return redirect(url_for('show_details', show_id=show_id))

@app.route('/shows/<show_id>/resume')
def show_resume(show_id):
    pass

@app.route('/shows/<show_id>/stop')
def show_stop(show_id):
    pass

@app.route('/shows/<show_id>/favorite')
def show_favorite(show_id):
    if session.get('username'):
        user = User.query.filter_by(username=session.get('username')).first()
        show = Show.query.filter_by(public_id=show_id).first()

        favorited = any(show_id == show.public_id for show in user.get_favorites())

        if not favorited:
            user.add_favorite(show)
            db.session.commit()

    return redirect(url_for('show_details', show_id=show_id))

@app.route('/shows/<show_id>/unfavorite')
def show_unfavorite(show_id):
    if session.get('username'):
        user = User.query.filter_by(username=session.get('username')).first()
        show = Show.query.filter_by(public_id=show_id).first()

        favorited = any(show_id == show.public_id for show in user.get_favorites())

        if favorited:
            user.remove_favorite(show)
            db.session.commit()

    return redirect(url_for('show_details', show_id=show_id))

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

    return render_template('show-add.html')

@app.route('/shows/<show_id>/edit', methods=['GET', 'POST'])
def show_edit(show_id):
    pass

@app.route('/shows/<show_id>/delete')
def show_delete(show_id):
    show = Show.query.filter_by(public_id=show_id).first()

    db.session.delete(show)
    db.session.commit()

    return redirect(url_for('shows'))

@app.route('/shows/<show_id>/episodes/<episode_id>')
def episode_details(show_id, episode_id):
    pass

@app.route('/shows/<show_id>/episodes/add', methods=['GET', 'POST'])
def episode_add(show_id):
    show = Show.query.filter_by(public_id=show_id).first()

    if request.method == 'POST':
        episode = Episode(
            request.form['title'],
            request.form['season'],
            request.form['number'],
            request.form['description'],
            show.id
        )

        db.session.add(episode)
        db.session.commit()

        return redirect(url_for('show_details', show_id=show_id))

    return render_template('episode-add.html')

@app.route('/shows/<show_id>/episodes/<episode_id>/edit')
def episode_edit(show_id, episode_id):
    pass

@app.route('/shows/<show_id>/episodes/<episode_id>/delete')
def episode_delete(show_id, episode_id):
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

if __name__ == '__main__':
    app.run()