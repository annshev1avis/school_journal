import datetime

from django.shortcuts import render


def show_test_page(request):
    context = {
        "uniq_stamp": datetime.datetime.now(),

    }
    return render(request, "tests/tests_list.html", context)
