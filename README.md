# backend_community_homework
Отчетная работа по заднию форм регистрации и логина

Используемые технологии:

Инструмент          | Версия
---------           | -------------
python              | 3.7 slim
django              | 2.2.16


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке


Cоздать и активировать виртуальное окружение:

```
py -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
py -m pip install --upgrade pip
```

```
py install -r requirements.txt
```

Выполнить миграции:

```
py manage.py migrate
```

Запустить проект:

```
py manage.py runserver
```
[![CI](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml)
