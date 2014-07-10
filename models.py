import re
from werkzeug.security import generate_password_hash
from app import db

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255), unique=True)
    season_count = db.Column(db.Integer)
    description = db.Column(db.Text)
    episodes = db.relationship('Episode', backref='show', lazy='dynamic')

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
    description = db.Column(db.Text)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

    def __init__(self, title, description, show_id):
        self.public_id = get_public_id(title)
        self.title = title
        self.description = description
        self.show_id = show_id

    def __repr__(self):
        return '<Episode %r>' % self.title

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

    def __repr__(self):
        return '<User %r>' % self.username

def get_public_id(title):
    public_id = re.sub(r'\s', '-', title)
    public_id = re.sub(r'[^A-Za-z0-9\-]', '', public_id)
    public_id = re.sub(r'--', '-', public_id)

    return public_id.lower()