from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from datetime import datetime


app = Flask(__name__)
app.config["SECRET_KEY"] = "eatery"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///nerdfoods.db"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
date = datetime.now()

def create_model():
	with app.app_context():
		db.create_all()
		return 'Database model created successfully'

class User(db.Model, UserMixin):
	id =  db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable=False)
	phone = db.Column(db.Integer, nullable=False)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)
	role = db.Column(db.String, default="User")
	order = db.relationship('Order', backref='user', cascade="all, delete-orphan")

class Item(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	image = db.Column(db.String)
	content = db.Column(db.String, nullable=False)
	category = db.Column(db.String, nullable=False)
	order = db.relationship('Order', backref="item", cascade="all, delete-orphan")

class Order(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	item_id = db.Column(db.Integer, db.ForeignKey("item.id", ondelete="CASCADE"))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
	date = db.Column(db.Date, default=date)
	quantity = db.Column(db.Integer, nullable=False)
	cost = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String, nullable=False)
	status = db.Column(db.String)
	
