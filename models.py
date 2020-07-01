from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

#Модель для хранения связей заказов и блюд
orders_meals_association = db.Table('orders_meals', \
db.Column('order_id', db.Integer, db.ForeignKey('orders.id')), \
db.Column('meal_id', db.Integer, db.ForeignKey('meals.id')))

#Модель для хранения заказов
class Order(db.Model):
    #Таблица
    __tablename__='orders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    meals = db.relationship('Meal', secondary=orders_meals_association)
    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Модель для хранения блюд
class Meal(db.Model):
    #Таблица
    __tablename__='meals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    picture = db.Column(db.String(50), nullable=False)
    orders = db.relationship('Order', secondary=orders_meals_association)
    category = db.relationship('Category')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))


#Модель для хранения категорий
class Category(db.Model):
    #Таблица
    __tablename__='categories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    meal = db.relationship('Meal')

#Модель для хранения Пользователей
class User(db.Model):
    #Таблица
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    orders = db.relationship('Order')
    
    @property
    def password(self):
    	# Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
    	# Устанавливаем пароль через этот метод
    	self.password_hash = generate_password_hash(password)
    
    def password_valid(self, password):
    	# Проверяем пароль через этот метод
    	# Функция check_password_hash превращает password в хеш и сравнивает с хранимым
    	return check_password_hash(self.password_hash, password)