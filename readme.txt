Пререквизиты
установите пакеты питон 3 из файла requirements
установите и настройте переменную окружения к базе данных PostgreSQL как описано в теории недели 4

Установка
1. из папки с app.py запускаем в терминале:
    flask db init
    flask db migrate
    flask db upgrade
    появятся 6 таблиц в PostgreSQL
2. запускаем скрипт fill_meald_categories.py чтобы загрузить блюда и категории

Запускаем flusk run и используем
