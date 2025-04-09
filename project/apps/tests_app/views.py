from django.shortcuts import render


def show_test_page(request):
    return render(request, "tests/tests_list.html", {})
