from flask import Flask, redirect, render_template, session, request, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets, os
import json
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from forms import RegistrationForm, LoginForm, ProductForm, CustomerForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,current_user,login_required,login_user,logout_user,UserMixin
from  flask_migrate import  Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/ecommerce'
app.config['SECRET_KEY'] = "asdfghj"
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate=Migrate(app,db)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message=u"please login first"


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).paginate(page=page, per_page=4)
    return render_template("display_items.html", products=products)


@app.route('/product/<int:id>')
def single_page(id):
    product = Product.query.get_or_404(id)
    return render_template('single_page.html', product=product)


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please log in first', 'danger')
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('index.html', title="Admin Page", products=products)


def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/addcart', methods=['GET', 'POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        product = Product.query.filter_by(id=product_id).first()
        if product_id and quantity and request.method == "POST":
            DictItem = {product_id: {'name': product.name, 'price': product.price, 'stock': product.stock,
                                     'discount': product.discount, 'quantity': quantity, 'image': product.image_1}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MergeDicts(session['Shoppingcart'], DictItem)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItem
                return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount'] / 100) * float(product['price'])
        subtotal = float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (.06 * float(subtotal)))
        grandtotal = float("%.2f" % (1.06 * subtotal))
    return render_template('carts.html', tax=tax, grandtotal=grandtotal)


@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    flash(f" Items updated")
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deletecartitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    profile = db.Column(db.String(80), unique=False, nullable=False,
                        default='profile.jpg')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(12), nullable=False)
    discount = db.Column(db.String(120), nullable=True)
    stock = db.Column(db.String(120), nullable=False)
    pub_date = db.Column(db.String(120), nullable=True)
    image_1 = db.Column(db.String(120), nullable=True, default="profile.jpg")
    image_2 = db.Column(db.String(120), nullable=True, default="profile.jpg")
    image_3 = db.Column(db.String(120), nullable=True, default="profile.jpg")

class JsonEncodeDict(db.TypeDecorator):
    impl=db.Text
    def process_bind_param(self,value,dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_value(self,value,dialect):
        if value is None:
            return {}
        else:
            return json.load(value)
class Customerorder(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    invoice=db.Column(db.String(20),unique=True,nullable=False)
    status = db.Column(db.String(20),default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    orders = db.Column(JsonEncodeDict)


@login_manager.user_loader
def user_loader(user_id):
    return Customer.query.get(user_id)

class Customer(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=False)
    country = db.Column(db.String(50), unique=False)
    state = db.Column(db.String(50), unique=False)
    city = db.Column(db.String(50), unique=False)
    contact = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(50), unique=False)
    zipcode = db.Column(db.Integer, unique=False)
    profile = db.Column(db.String(50), unique=False, default='profile.jpg')
    date_created = db.Column(db.String(50))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(name=form.name.data, username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data}Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('register_user.html', form=form, title="Registration page")


@app.route('/customer', methods=['POST', 'GET'])
def customer():
    form = CustomerForm()
    if form.validate_on_submit():
        entry = Customer(name=form.name.data, username=form.username.data, contact=form.contact.data,
                         email=form.email.data, password=form.password.data, country=form.country.data,
                         state=form.state.data, city=form.city.data, address=form.address.data,
                         zipcode=form.zipcode.data, profile=form.profile.data, date_created=datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash(f' Thank you for registering !!!!!!!!!!!!!!', 'success')
        return redirect(url_for('login'))
    return render_template('customer_register.html', form=form)
@app.route('/customer_login',methods=['GET','POST'])
def customerLogin():
    form=LoginForm(request.form)
    if form.validate():
        user=Customer.query.filter_by(email=form.email.data).first()
        if (user and user.password == form.password.data):
            login_user(user)
            flash(f'You are login now !!!!!','success')
            next=request.args.get('next')
            return redirect(next or url_for('home'))
        flash(f'Incorrect Email nd Password','danger')
        return redirect(url_for('customerLogin'))
    return render_template('admin_login.html',form=form)
@app.route('/customer_logout')
def customer_logout():
    logout_user()
    return  redirect(url_for('customerLogin'))

@app.route('/getorder')
@login_required
def getorder():
    if current_user.is_authenticated:
        customer_id=current_user.id
        invoice=secrets.token_hex(5)
        try:
            order=Customerorder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash(f'Your Order has been placed','success')
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash(f'Something went wrong while getting order......!!!','danger')
            return  redirect(url_for('getCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal=0
        subTotal=0
        customer_id=current_user.id
        customer=Customer.query.filter_by(id=customer_id).first()
        orders=Customerorder.query.filter_by(customer_id=customer_id).first()
        for _key,product in orders.orders.items():
            discount=(product['discount']/100)*float(product['price'])
            subTotal=float(product['price'])*int(product['quantity'])
            subTotal-=discount
            tax=("%.2f" % (0.6 * float(subTotal)))
            grandTotal=float("%.2f" % (1.06 * subTotal))
    else:
        return  redirect(url_for('customerLogin'))
    return render_template('order.html',invoice=invoice,tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if (user and user.password == form.password.data):
            session['email'] = form.email.data
            flash(f'Welcome {form.email.data} You are logged now', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong Password please try again ........', 'danger')
    return render_template('admin_login.html', form=form, title="Login Page")


@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    form = ProductForm(request.form)
    if (request.method == "POST"):
        name = request.form.get("name")
        price = request.form.get("price")
        discount = request.form.get("discount")
        stock = request.form.get("stock")
        description = request.form.get("description")
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get("image_2"), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get("image_3"), name=secrets.token_hex(10) + ".")
        # image_1=request.form.get("image_1")
        # image_2 = request.form.get("image_2")
        # image_3 = request.form.get("image_3")

        entry = Product(name=name, price=price, stock=stock, discount=discount, description=description,
                        pub_date=datetime.now(),
                        image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(entry)
        db.session.commit()
        flash(f'The Product is added', 'success')
        return redirect(url_for('admin'))

    return render_template("addproduct.html", form=form, title="Add Product")


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    form = ProductForm(request.form)
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.discount = form.discount.data
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        db.session.commit()
        flash(f'Your product has been updated', 'success')
        return redirect(url_for('admin'))
    else:
        form.name.data = product.name
        form.price.data = product.price
        form.discount.data = product.discount
        form.stock.data = product.stock
        form.description.data = product.description

    return render_template("updateproduct.html", form=form, product=product)


@app.route('/deleteproduct/<int:id>', methods=['GET', "POST"])
def deleteproduct(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))

            except Exception as e:
                print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f' Your Product has been deleted', 'success')
        return redirect(url_for('admin'))
    flash(f' Cant delete product', 'danger')
    return render_template()


if __name__ == "__main__":
    app.run(debug=True)
