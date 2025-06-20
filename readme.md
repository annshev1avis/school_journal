# 📌 Электронный журнал для "Rybakov PlaySchool"

Это приложение было создано по запросу московской школы Rybakov PlaySchool, 
реализующей прогрессивную модель развивающего обучения. В рамках этой модели
ежемесячные проверочные работы полностью заменяют традиционную систему оценивания. 
Особенностями проверочных являются переменное количество заданий, изменяющаяся шкала баллов, 
а также наличие двух уровней сложности.

Главные функции:
- сохранение выставленных оценок
- валидация данных
- составление личных отчётов
- визуализация успеваемости в виде графиков

Благодаря этому приложению школа сокращает время на выполнение рутинных задач, 
освобождая учителей для самого важного — качественного обучения детей

---

## 🔧 Технологии

- Python
- Django
- (a little bit): vanilla JS

---

## 🚀 Установка



### Установить Pango - зависимость библиотеки weasyprint (формирование pdf)
для Windows:
1. Установить программу https://www.msys2.org/#installation
2. Выполнить установку ВЕЗДЕ сохраняя значения по умолчанию
3. Открыть приложение msys2 (консольный интерфейс) и выполнить команду
```pacman -S mingw-w64-x86_64-pango```
4. Закрыть консоль

для Linux:
```bash
# Debian/Ubuntu:
sudo apt install libpango1.0-0
```

для MacOS:
```bash
brew install pango
```

### Создать файл .env
Создать файл на основе .env_example и внести в него актуальные данные  

### Выполнить команды
для Windows:
```bash
# Клонировать репозиторий
git clone https://github.com/annshev1avis/school_journal

# (далее команды выполнять в корневом каталоге проекта)
# Cоздать и активать виртуальное окружение
py -m venv venv
venv/Scripts/activate

# Установить зависимости
pip install -r requirements_dev.txt

# Перейти в каталог project
cd project

# Выполнить миграции (создать базу данных с необходимой структурой)
py manage.py migrate

# Создать суперпользователя (учетная запись с которой можно войти 
# не только в приложение для обычных пользователей, но и админку)
py manage.py createsuperuser --username=joe --email=joe@example.com
```

для Linux/MacOS:
```bash
# Клонировать репозиторий
git clone https://github.com/annshev1avis/school_journal

# Перейти в корень проекта
cd school_journal

# Создать и активировать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements_dev.txt

# Перейти в каталог project
cd project

# Выполнить миграции (создать базу данных с необходимой структурой)
python manage.py migrate

# Создать суперпользователя (учетная запись с которой можно войти 
# не только в приложение для обычных пользователей, но и админку)
python manage.py createsuperuser --username=joe --email=joe@example.com
```

# ▶️ Запуск
для Windows:
```bash
py manage.py runserver
```
для Linux/MacOS:
```bash
py manage.py runserver
```