from flask import Flask, render_template, redirect, flash, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from webform import AdminForm, UserForm, LoginForm, MealForm, OrderForm, ChatForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid as uuid
from PIL import Image
import io


date = datetime.now()
FILE_FOLDER = "static/files/"
if not os.path.exists(FILE_FOLDER):
	os.makedirs(path)

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
app.config["FILE_FOLDER"] = FILE_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
	if session['account'] == 'Admin':
		return Admin.query.get(int(id))
	elif session['account'] == 'User':
		return User.query.get(int(id))
	else:
		return None
		

class Admin(db.Model, UserMixin):
	id =  db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)


class User(db.Model, UserMixin):
	id =  db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)
	order = db.relationship('Order', backref='user', cascade="all, delete-orphan")
	chat = db.relationship("Chat", backref="user", cascade="all, delete-orphan")
	

class Order(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	time = db.Column(db.String, default=date.strftime('%I:%M %p - %B %d, %Y'))
	meal_id = db.Column(db.Integer, db.ForeignKey('menu.id', ondelete="CASCADE"))
	quantity = db.Column(db.String, nullable=False)
	comment = db.Column(db.String, nullable=True)
	location = db.Column(db.String, nullable=False)
	status = db.Column(db.String, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
	

class Menu(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	dish = db.Column(db.String, nullable=False)
	image = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	order = db.relationship('Order', backref="menu", cascade="all, delete-orphan")


class Chat(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
	text = db.Column(db.String)
	image = db.Column(db.String)
	admin = db.Column(db.String)
	datetime = db.Column(db.String, default=date.strftime('%I:%M %p'))






def crop_image(img):
	image = Image.open(io.BytesIO(img))
	width, height = image.size
	if width == height:
	   return image
	offset  = int(abs(height-width)/2)
	if width>height:
		image = image.crop([offset,0,width-offset,height])
	else:
		image = image.crop([0,offset,width,height-offset])
	return image


@app.context_processor
def base():
	time = date.strftime('%Y')
	orders = Order.query.all()
	num = []
	for order in orders:
		if order.status:
			pass
		else:
			num.append(order.status)
	return dict(time=time, num=len(num),session=session)



@app.route('/chats')
@login_required
def chats():
	chats = Chat.query.group_by(Chat.user_id)
	return render_template("chats.html", chats=chats)



@app.route('/chat/<int:id>', methods=["POST", "GET"])
@login_required
def chat(id):
	form = ChatForm()
	chat = Chat.query.filter_by(user_id=id)
	if request.method == "POST":
		text = Chat(user_id=id, text=form.text.data, admin=request.form["name"])
		db.session.add(text)
		db.session.commit()
		form.text.data = ""
	return render_template("chat.html", chats=chat, form=form, session=session)



@app.route('/', methods=["POST", "GET"])
def menu():
	form = MealForm()
	menus = Menu.query.order_by(-Menu.id)

	if form.validate_on_submit():
		if form.image.data:
			file = secure_filename(form.image.data.filename)
			file_name = str(uuid.uuid1()) + "_"+ file
			image = crop_image(form.image.data.read())
			image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
			meal = Menu(dish=form.dish.data, price=form.price.data, image=file_name)
		else:
			meal = Menu(dish=form.dish.data, price=form.price.data, image=form.image.data.read())
		db.session.add(meal)
		db.session.commit()
		form.dish.data = ""
		form.price.data = ""
		form.image.data = ""
	return render_template("menu.html", menus=menus, session=session, form=form)
	


@app.route('/order/<int:id>', methods=["POST", "GET"])
@login_required
def order(id):
	if session['account'] == 'User':
		order = Order.query.filter_by(user_id=id).order_by(-Order.id)
		return render_template("order.html", orders=order)
	users = Order.query.order_by(-Order.id)
	return render_template("order.html", users=users)


@app.route('/edit-price/<int:id>', methods=["POST", "GET"])
@login_required
def edit_price(id):
	form = MealForm()
	meal = Menu.query.filter_by(id=id).first()
	if request.method == "POST":
		meal.price = form.price.data
		db.session.add(meal)
		db.session.commit()
		return redirect(url_for("menu"))
	form.price.data = meal.price
	return render_template("edit_price.html", form=form)
	
	
	
@app.route('/make-order/<int:id>', methods=["POST", "GET"])
@login_required
def make_order(id):
	form = OrderForm()
	menu = Menu.query.filter_by(id=id).first()
	
	if form.validate_on_submit():
		order = Order(meal_id=id, quantity=form.quantity.data, location=form.location.data, comment=form.comment.data,  user_id=current_user.id)
		try:
			db.session.add(order)
			db.session.commit()
			flash("Your order is placed successfully...")
			return redirect(url_for('order', id=current_user.id))
		except:
			flash("An error occurred, order was not placed. Try again...")
	return render_template("make_order.html",form=form,menu=menu)
	
	
	
@app.route('/login', methods=["POST", "GET"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			password = form.password.data
			data = check_password_hash(user.password, password)
			if data == True:
				login_user(user)
				session["account"] = "User"
				return redirect("/")
			else:
				flash("Password is incorrect")
		else:
			flash("User does not exist")
	return render_template("login.html", form=form)
	
	
	
@app.route('/signup', methods=["POST", "GET"])
def signup():
	form = UserForm()
	if form.validate_on_submit():
		user = User(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data))
		try:
			db.session.add(user)
			db.session.commit()
			flash("Sign up was successful")
			return redirect("/login")
		except:
			flash("An error occurred, User not added. Try again...")
	return render_template("signup.html", form=form)



@app.route('/edit-user/<int:id>', methods=["POST", "GET"])
@login_required
def edit_user(id):
	form = UserForm()
	user = User.query.filter_by(id=id).first()
	if request.method == "POST":
		if check_password_hash(user.password, form.password.data) == True:
			user.name = form.name.data
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('order', id=id))
		else:
			flash("Password is incorrect, try again...")
	form.name.data = user.name
	return render_template("edit_user.html", form=form)



@app.route('/admin-login', methods=["POST", "GET"])
def admin_login():
	form = AdminForm()
	if form.validate_on_submit():
		admin = Admin.query.filter_by(username=form.username.data).first()
		if admin:
			if check_password_hash(admin.password, form.password.data) == True:
				login_user(admin)
				session["account"] = "Admin"
				return redirect("/")
			else:
				flash("Password is incorrect")
		else:
			flash("Admin does not exist")
	return render_template("admin_login.html", form=form)



@app.route('/admin', methods=["POST", "GET"])
def admin():
	form = AdminForm()
	if form.validate_on_submit():
		admin = Admin(username=form.username.data,password=generate_password_hash(form.password.data))
		try:
			db.session.add(admin)
			db.session.commit()
			flash("Sign up was successful")
		except:
			flash("An error occurred, Admin not added. Try again...")
	return render_template("admin.html", form=form)



@app.route("/detail/<int:id>", methods=["POST", "GET"])
@login_required
def detail(id):
	order = Order.query.filter_by(id=id).first()
	cost = int(order.menu.price) * int(order.quantity)
	if request.method == "POST":
		order.status = request.form["status"]
		db.session.add(order)
		db.session.commit()
	return render_template("detail.html", order=order, cost=cost)
		

	
@app.route('/logout')
def logout():
	logout_user()
	flash("You have been logged out")
	return redirect("/")
	
	
@app.route("/del-meal/<int:id>")
def del_meal(id):
	meal = Menu.query.filter_by(id=id).first()
	if meal.image:
		os.remove('static/files/' + meal.image)
	db.session.delete(meal)
	db.session.commit()
	return redirect(url_for("menu"))



@app.route("/del-order/<int:id>")
def del_order(id):
	order = Order.query.filter_by(id=id).first()
	db.session.delete(order)
	db.session.commit()
	return redirect(url_for("order", id=current_user.id))

