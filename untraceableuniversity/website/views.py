from django.shortcuts import render
from .models import *
from django.contrib import messages

# We want to give people a cookie-less experience so we turn off CSRF
# by default (we don't have many forms anyways)
from django.views.decorators.csrf import csrf_exempt

# For sending mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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
    if request.method == "POST":
        subject = "Joining the Untraceable University project"
        mailcontext = {
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "institution": request.POST.get("institution"),
            "discipline": request.POST.get("discipline"),
            "message": request.POST.get("message"),
        }
        msg = render_to_string("mailbody/join.txt", mailcontext)
        email = EmailMultiAlternatives(
            subject,
            msg,
            "info@untraceable-university.org",
            ["info@untraceable-university.org"],
            reply_to=[request.POST.get("email")],
        )
        email.send()
        messages.success(request, "Thanks, we have received your information. We will get back to you within a few days.")

    context = {
        "info": get_page("join"),
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

@csrf_exempt
def contact(request):
    if request.method == "POST":
        subject = "Untraceable University contact form"
        mailcontext = {
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "message": request.POST.get("message"),
        }
        msg = render_to_string("mailbody/join.txt", mailcontext)
        email = EmailMultiAlternatives(
            subject,
            msg,
            "info@untraceable-university.org",
            ["info@untraceable-university.org"],
            reply_to=[request.POST.get("email")],
        )
        email.send()
        messages.success(request, "Thanks, we have received your information. We will get back to you within a few days.")

    context = {
        "info": get_page("contact"),
        "menu": "contact",
    }

    return render(request, "contact.html", context)

