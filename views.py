import datetime
from flask import render_template, session, redirect, request
from  sqlalchemy.sql.expression import func
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import app, db
from models import User, Order, Category, Meal
from forms import OrderForm, RegistrationForm, LoginForm

#получаем корзину из сессии
def get_cart_from_session():
    cart = session.get("cart", [])
    cart_count = 0
    cart_amount = 0
    for id in cart:
        cart_amount += db.session.query(Meal).filter(Meal.id == id).scalar().price
        cart_count += 1
    return cart, cart_count, cart_amount

#Главная страница
@app.route('/')
def home():
    #грузим категории
    categories = db.session.query(Category).order_by(Category.id.desc()).all()
    
    #грузим рандомные блюда для категорий
    cat_meals = []
    for cat in categories:
        cat_meals.append([cat.id, cat.title,\
         db.session.query(Meal).\
         filter(Meal.category_id == cat.id).order_by(func.random()).limit(3)])

    #получим пользователя из сессии
    current_user = session.get('user', '')

    #грузим текущую корзину из сессии
    _, cart_count, cart_amount = get_cart_from_session()

    output = render_template('main.html', cat_meals=cat_meals, cart_amount=cart_amount,\
     cart_count=cart_count, current_user=current_user)
    return output

#Добавление в корзину блюда с главной страницы
@app.route('/addtocart/<int:id>/')
def add_to_cart(id):
    # Получаем либо значение из сессии, либо пустой список
    cart = session.get("cart", [])
    
    #проверка, что ранее такое блюдо не добавляли в корзину
    if cart.count(id)>0:
        err_msg = 'Ввиду большего спроса добавить в корзину можно только 1 экземпляр блюда'
        return render_template('cart_error.html', err_msg=err_msg)

    # Добавлям элемент в список
    cart.append(id)
    # Записываем список обратно в сессию
    session['cart'] = cart
    return redirect('/')

#Удаление блюда из корзины в корзине
@app.route('/delfromcart/<int:id>/')
def del_from_cart(id):
    # Получаем либо значение из сессии, либо пустой список
    cart = session.get("cart", [])
    
    # Удалим блюдо элемент в список
    cart.remove(id)
    # Записываем список обратно в сессию
    session['cart'] = cart
    # флаг, чтобы корзине дать понять необходимость отобразить, что блюдо удалено
    session['is_meal_del'] = True
    return redirect('/cart/')

#Корзина
@app.route('/cart/',  methods=["GET", "POST"])
def get_cart():
    #получим пользователя из сессии
    current_user = session.get('user', '')

    #грузим текущую корзину из сессии
    cart, cart_count, cart_amount = get_cart_from_session()
    
    #список заказа
    cart_list = []
    if cart_count > 0:
        cart_list = db.session.query(Meal).filter(Meal.id.in_(cart)).all()
 
    form = OrderForm()
    if form.validate_on_submit() and (request.method == "POST"):
        new_order = Order(
            name = form.name.data,
            mail = form.mail.data,
            date = datetime.datetime.now(),
            amount = cart_amount,
            status = 'заказ отправлен',
            phone = form.phone.data,
            address = form.address.data)
        for id in cart:
            meal_to_order = db.session.query(Meal).filter(Meal.id == id).scalar()
            new_order.meals.append(meal_to_order)
        db.session.add(new_order)
        db.session.commit()
        session['cart'] = []
        return redirect('/ordered/')
    
    #Удалялось ли блюдо
    is_meal_del = session.get('is_meal_del', False)
    if is_meal_del:
        session['is_meal_del'] = False
    

    output = render_template('cart.html', cart_amount=cart_amount, cart_count=cart_count,\
     form=form, current_user=current_user, cart_list=cart_list, is_meal_del=is_meal_del)
    return output

#Личный кабинет
@app.route('/account/')
def get_account():
    #получим пользователя из сессии
    current_user = session.get('user', '')
    
    #проверим, что пользователь авторизован
    if current_user == '':
        return redirect('/login/')

    #грузим текущую корзину из сессии
    _, cart_count, cart_amount = get_cart_from_session()

    #получим историю заказов пользователя
    orders = db.session.query(Order).filter(Order.mail == current_user['mail'])
    count_orders = 0
    for i in orders:
        count_orders+=1

    #получим приветствие для пользователя из сессии
    welcome = session.pop("welcome", 'С возвращением!')

    output = render_template('account.html', welcome=welcome, cart_amount=cart_amount,\
     cart_count=cart_count, current_user=current_user, orders=orders, count_orders=count_orders)
    return output

#Для аутентификации
@app.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and (request.method == "POST"):
        user = User.query.filter_by(mail=form.mail.data).first()
        if not user:
            form.mail.errors.append("Пользователь с таким Email не обнаружен")
            return render_template("auth.html", form=form)
        else:
            if not user.password_valid(form.password.data):
                form.password.errors.append("Неверный пароль")
                return render_template("auth.html", form=form)
            else:
                session["user"] = {
                    "id": user.id,
                    "mail": user.mail
                    #"role": user.role,
                }
                return redirect('/account/')
            
    return render_template('auth.html', form=form)

#Для регистрации
@app.route('/register/', methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit() and (request.method == "POST"):
        user = User.query.filter_by(mail=form.mail.data).first()
        if user:
            form.mail.errors.append("Пользователь с таким Email уже существует")
            return render_template("register.html", form=form)
        new_user = User(
            mail=form.mail.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        session["user"] = {
                    "id": new_user.id,
                    "mail": new_user.mail
                    #"role": user.role,
                }

        session['welcome']='Поздравляем с созданием личного кабинета!'
        return redirect('/account/')



    return render_template('register.html', form=form)

#Для разлогирования
@app.route('/logout/', methods=["GET", "POST"])
def logout():
    session.pop('user')
    return redirect('/login/')

#Для подтверждения отправки закака
@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')

#просили добавить админку, но тут нет контроля доступа
class MyUserView(ModelView):

  # Настройка общего списка

  column_exclude_list = ['password_hash']  # убрать из списка одно или несколько полей
  column_searchable_list = ['mail']  # добавить поиск по полям
  #column_filters = ['country'] # добавить фильтр по полям

  # Права на CRUD операции
    
  can_create = False  
  can_edit = False
  can_delete = False

    
  # Лимит записей на страницу
    
  page_size = 50

admin = Admin(app)

admin.add_view(MyUserView(User, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Meal, db.session))
admin.add_view(ModelView(Order, db.session))