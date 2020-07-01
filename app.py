from flask import Flask
from flask_migrate import Migrate

from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# Настраиваем соединение
db.init_app(app)

# Создаем объект поддержки миграций
migrate = Migrate(app, db)


# Имортируем представление
from views import *
    
    
if __name__ == "__main__":
    app.run()