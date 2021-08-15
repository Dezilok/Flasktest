from flask import Flask, redirect, render_template, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user, Security, SQLAlchemyUserDatastore, UserMixin
from flask_sqlalchemy import SQLAlchemy

# Instantiate the Flask application with configurations
app = Flask(__name__)
# Configure a specific Bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'sandstone'
app.config['SECRET_KEY'] = 'secretkey'
app.config['SECURITY_PASSWORD_SALT'] = 'none'
# Configure application to route to the Flask-Admin index view upon login
app.config['SECURITY_POST_LOGIN_VIEW'] = '/admin/'
# Configure application to route to the Flask-Admin index view upon logout
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/admin/'
# Configure application to route to the Flask-Admin index view upon registering
app.config['SECURITY_POST_REGISTER_VIEW'] = '/admin/'
app.config['SECURITY_REGISTERABLE'] = True
# Configure application to not send an email upon registration
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Instantiate the database
db = SQLAlchemy(app)

# Create a table of users and user roles
roles_users_table = db.Table('roles_users',
                             db.Column('users_id', db.Integer(), db.ForeignKey('users.id')),
                             db.Column('roles_id', db.Integer(), db.ForeignKey('roles.id')))


# Define models for the users and user roles
class Roles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(80))
    active = db.Column(db.Boolean())

    roles = db.relationship('Roles', secondary=roles_users_table, backref='user', lazy=True)


# Create a datastore and instantiate Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
security = Security(app, user_datastore)


# Create the tables for the users and roles and add a user to the user table
# Only needed for first run
# @app.before_first_request
# def create_user():
#     db.drop_all()
#     db.create_all()
#     user_datastore.create_user(email='admin', password='admin')
#     db.session.commit()


# Instantiate Flask-Admin
admin = Admin(app, name='Admin', base_template='my_master.html', template_mode='bootstrap3')


# Base model with access control for admin
class AccessView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))


# Create a ModelView to add to our administrative interface
class UserModelView(AccessView):
    column_list = ['email', 'password']


# Add administrative views to Flask-Admin
admin.add_view(UserModelView(Users, db.session))


# Add the context processor
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        get_url=url_for,
        h=admin_helpers
    )


# Define the index route
@app.route('/')
def index():
    return render_template('index.html')


# Models for db
class Product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40))
    color = db.Column(db.String(80))
    price = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    order = db.relationship('Order', backref='product', lazy=True)


class Address(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(80))
    city = db.Column(db.String(80))
    street = db.Column(db.String(255))
    order = db.relationship('Order', backref='address', lazy=True)


class Order(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


# Views for Flask-Admin
class ProductModelView(AccessView):
    column_list = ['name', 'color', 'price', 'weight']


class AddressModelView(AccessView):
    column_list = ['country', 'city', 'street', 'order']
    column_filters = ('country', 'city', 'street')


class OrderModelView(AccessView):
    column_list = ['address_id', 'product_id']


# Add administrative views to Flask-Admin
admin.add_view(ProductModelView(Product, db.session))
admin.add_view(AddressModelView(Address, db.session))
admin.add_view(OrderModelView(Order, db.session))


if __name__ == '__main__':
    # Start app
    app.run()




