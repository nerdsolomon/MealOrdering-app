from flask import render_template, redirect, flash, request, session, url_for, send_from_directory
from model import app, db, date, User, Order, Item, Chat
from functions import crop_image, allowed_file, ALLOWED_EXTENSIONS
from webform import Forms
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "home"

@login_manager.user_loader
def load_user(id):
	if session:
		return User.query.get(int(id))
	else:
		return None

FILE_FOLDER = "static/storage"
if not os.path.exists(FILE_FOLDER):
	os.makedirs(FILE_FOLDER)
app.config["FILE_FOLDER"] = FILE_FOLDER

def store(var):
    db.session.add(var)
    db.session.commit()
    
def remove(var):
    db.session.delete(var)
    db.session.commit()
            
            
@app.context_processor
def base():
    time = date.strftime('%Y')
    account = session.get("account")
    if current_user.is_authenticated and account:
        if account == "Admin":
            return dict(account=account, time=time)
        elif account == "User":
            return dict(account=account, time=time)
    return dict(time=time)


@app.route('/', methods=["POST", "GET"])
def home():
    form = Forms()
    if request.method == "POST":
        form_type = request.form["nan"]
        if form_type == "signin":
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    if user.role == "Admin":
                        session["account"] = "Admin"
                    else:
                        session["account"] = "User"
                else:
                    flash("Password is incorrect")
            else:
                flash("User does not exist")
        elif form_type == "signup":
            user = User(name=form.string.data, phone=form.number.data, email=form.email.data, password=generate_password_hash(form.password.data))
            store(user)
    form.string.data, form.email.data, form.number.data, form.password.data = "","","",""
    return render_template("home.html", form=form)


@app.route('/signout')
@login_required
def signout():
	logout_user()
	return redirect('/')

    
@app.route("/items/<category>")
def items(category):
    items = Item.query.order_by(-Item.id).filter_by(category=category)
    return render_template("items.html", items=items)
    
    
@app.route('/item/<int:id>', methods=["POST", "GET"])
def item(id):
    form = Forms()
    item = Item.query.filter_by(id=id).first()
    if request.method == "POST":
        order = Order(item_id=id, user_id=current_user.id, quantity=form.number.data, description=form.text.data)
        store(order)
        flash('Your order is placed.')
        return redirect(url_for("cart", id=current_user.id))
    return render_template("item.html", item=item, form=form)
    
   
@app.route("/menu/setting", methods=["POST", "GET"])
def menu_setting():
    form = Forms()
    items = Item.query.order_by(-Item.id)
    if request.method == "POST":
        form_type = request.form["nan"]
        if form_type == "add":
            file = secure_filename(form.file.data.filename)
            file_name = str(uuid.uuid1()) + "_"+ file
            image = crop_image(form.file.data.read())
            image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
            item = Item(name=form.string.data, price=form.number.data, image=file_name, content=form.text.data, category=request.form["type"])
            store(item)
        elif form_type == "edit":
            item = Item.query.filter_by(id=request.form["id"]).first()
            item.name = form.string.data
            item.price = form.number.data
            item.category = request.form["type"]
            item.content = form.text.data
            store(item)
    return render_template("menu_setting.html", items=items, form=form)
 
 
@app.route('/members', methods=["POST", "GET"])
def members():
    form = Forms()
    members = User.query.order_by(User.id)
    if request.method == "POST":
        admin = User.query.filter_by(id=request.form["id"]).first()
        admin.role = request.form["role"]
        store(admin)
    return render_template("members.html", members=members, form=form)


@app.route('/chats')
def chats():
	chats = Chat.query.group_by(Chat.user_id).order_by(-Chat.id)
	return render_template("chats.html", chats=chats)


@app.route('/chat/<int:id>', methods=["POST", "GET"])
def chat(id):
	form = Forms()
	chats = Chat.query.filter_by(user_id=id)
	if request.method == "POST":
		chat = Chat(user_id=id, admin=form.string.data, text=form.text.data, image=form.file.data)
		store(chat)
	form.text.data = ""
	return render_template("chat.html", chats=chats, form=form)


@app.route("/user/profile/<int:id>", methods=['POST', 'GET'])
@login_required
def profile(id):
    form = Forms()
    user = User.query.filter_by(id=id).first()

    if request.method == "POST":
        action_type = request.form["name"]
        if action_type == "profile":
            if check_password_hash(user.password, form.password.data):
                user.name = form.string.data
                user.phone = form.number.data
                user.email = form.email.data
                store(user)
                flash("Profile editted")
            else:
                flash("Password incorrect")
        elif action_type == "password":
            if check_password_hash(user.password, form.old.data):
                if form.password.data == form.check.data:
                    user.password = generate_password_hash(form.password.data)
                    store(user)
                    flash("Password updated")
                else:
                    flash("Passwords don't match")
            else:
                flash("Old password is incorrect")
    form.string.data, form.email.data, form.number.data = user.name, user.email, user.phone 
    return render_template("profile.html", form=form)
    

@app.route('/carts', methods=["POST", "GET"])
def carts():
	carts = Order.query.order_by(-Order.id)
	if request.method == "POST":
	    cart = Order.query.filter_by(id=request.form["id"]).first()
	    cart.status = request.form["status"]
	    store(cart)
	return render_template("carts.html", carts=carts)


@app.route('/cart/<int:id>')
def cart(id):
	carts = Order.query.filter_by(user_id=id).order_by(-Order.id)
	return render_template("cart.html", carts=carts)


@app.route('/cart/delete/<int:id>')
@login_required
def cart_delete(id):
    cart = Order.query.filter_by(id=id).first()
    remove(cart)
    return redirect(url_for("cart", id=current_user.id))
    
    
@app.route('/user/delete/<int:id>')
@login_required
def user_delete(id):
    user = User.query.filter_by(id=id).first()
    remove(user)
    return redirect(url_for("members"))
    
    
@app.route('/item/delete/<int:id>')
@login_required
def item_delete(id):
    item = Item.query.get(id)
    if item.image:
        file_path = os.path.join(app.config["FILE_FOLDER"], item.image)
        os.remove(file_path)
    remove(item)
    return redirect(url_for("menu_setting"))