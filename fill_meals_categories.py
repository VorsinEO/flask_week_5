import os
import csv

from app import app, db
from models import Category, Meal
app.app_context().push()
#Заполним таблицу категорий
if  db.session.query(Category).get(1):
    print('Вы пытаетесь выполнить инициирующую загрузку категорий повторно, очистите таблицы чтобы ее выполнить')
else:
    file_to_open = os.path.expanduser('~/projects/spepik_flask/week_5_project/flask_week_5/data/categories.csv')
    with open(file_to_open) as file:
        reader = csv.DictReader(file)
        for category in reader:
            category_add = Category(id=category['id'], title=category['title'])
            db.session.add(category_add)
        db.session.commit()

#Заполним таблицу блюд
if  db.session.query(Meal).get(1):
    print('Вы пытаетесь выполнить инициирующую загрузку блюд повторно, очистите таблицы чтобы ее выполнить')
else:
    file_to_open = os.path.expanduser('~/projects/spepik_flask/week_5_project/flask_week_5/data/meals.tsv')
    with open(file_to_open) as file:
        reader = csv.DictReader(file, delimiter='\t')
        for meal in reader:
            meal_add = Meal(id=meal['id'], title=meal['title'], price=meal['price'],\
            description=meal['description'], picture = meal['picture'])
            cat=db.session.query(Category).filter(Category.id == meal['category_id']).scalar()
            meal_add.category = cat
            db.session.add(meal_add)
        db.session.commit()