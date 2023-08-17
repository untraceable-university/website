from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import *

def get_page(slug):
    return PageContent.objects.get(slug=slug)

@csrf_exempt
def index(request):
    context = {
    }

    return render(request, "index.html", context)

@csrf_exempt
def join_us(request, slug):
    context = {
        "info": get_page(slug),
    }

    return render(request, "join.html", context)

