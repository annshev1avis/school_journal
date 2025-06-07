import re
from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    always_allowed_urls = [
        reverse("users:login"),
        "/admin/"
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.compile_urls()

    def compile_urls(self):
        self.always_allowed_urls = [
            re.compile(f"^{re.escape(url)}") for url in self.always_allowed_urls
        ]

    def is_always_allowed(self, path):
        for url_pattern in self.always_allowed_urls:
            if url_pattern.match(path):
                return True
        return False

    def __call__(self, request):
        if not request.user.is_authenticated and not self.is_always_allowed(request.path):
            return redirect(reverse("users:login"))
        return self.get_response(request)