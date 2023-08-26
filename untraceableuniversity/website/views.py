from django.shortcuts import render

# We want to give people a cookie-less experience so we turn off CSRF
# by default (we don't have many forms anyways)
from django.views.decorators.csrf import csrf_exempt

from .models import *

def get_page(slug):
    return PageContent.objects.get(slug=slug)

@csrf_exempt
def index(request):
    context = {
        "menu": "home",
        "inspiration": Inspiration.objects.all(),
        "teaching": get_page("teaching"),
        "research": get_page("research"),
    }

    return render(request, "home.html", context)

@csrf_exempt
def join_us(request, slug="join"):
    context = {
        "info": get_page(slug),
        "menu": "join_us",
    }

    return render(request, "join.html", context)

@csrf_exempt
def page(request, slug):
    context = {
        "info": get_page(slug),
        "menu": slug,
    }

    return render(request, "page.html", context)


@csrf_exempt
def templates(request):
    return render(request, "templates.html")
