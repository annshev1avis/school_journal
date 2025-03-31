import datetime

from django.http import HttpResponse
from django.shortcuts import render


def show_test_page(request):
    context = {
        "campuses": ["Кутузовский", "Саларьево", "Дегунино"],
        "classes": ["1 А", "1 Б", "2 А", "2 Б", "3", "4 А", "4 Б"],
        "subjects": [
            "Русский язык", "Математика",
            "Литериатурное чтение", "Окружающий мир",
        ],
        "students": [
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
            {"surname": "Шевченко", "name":"Ника"},
            {"surname": "Мухамедов", "name": "Артем"},
            {"surname": "Хусаинова", "name": "Диана"},
        ],
        "dates": [i for i in range(60)],
        "tests": [
            {"name": "Проверочная декабрь", "date": None, "id": 6},
            {"name": "Мониторинг ноябрь", "date": datetime.date(2024, 11, 25), "id": 5},
            {"name": "Проверочная ноябрь", "date": datetime.date(2024, 11, 3), "id": 4},
            {"name": "Проверочная октябрь", "date":datetime.date(2024, 10, 10), "id": 3},
            {"name": "Мониторинг сентябрь", "date": datetime.date(2024, 9, 29), "id": 2},
            {"name": "Стартовая проверочная", "date": datetime.date(2024, 9, 5), "id": 1},
        ]
    }
    return render(request, "marks/main_page.html", context)
