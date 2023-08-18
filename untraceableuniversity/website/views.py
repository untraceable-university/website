from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import *

def get_page(slug):
    return PageContent.objects.get(slug=slug)

@csrf_exempt
def index(request):
    context = {
        "menu_transparent": True,
        "menu": "home",
    }

    return render(request, "index.html", context)

@csrf_exempt
def join_us(request, slug="join"):
    context = {
        "info": get_page(slug),
        "menu": "join",
    }

    return render(request, "join.html", context)

@csrf_exempt
def page(request, slug):
    context = {
        "info": get_page(slug),
        "menu": slug,
    }

    return render(request, "page.html", context)

