from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# We want to give people a cookie-less experience so we turn off CSRF
# by default (we don't have many forms anyways)
from django.views.decorators.csrf import csrf_exempt

# For sending mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# For the translations
from django.utils.translation import gettext_lazy as _

# For the control panel
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import modelform_factory, modelformset_factory

def get_page(request, slug):
    try:
        return PageContent.objects.get(slug=slug, language__language_code=request.language)
    except ObjectDoesNotExist:
        # When linking pages in templates, we use English slugs. So if the PageContent is not found, we try
        # to get the English Page, and get the PageContent for that particular language. Not greatly efficient
        # but it does the trick. We use canonical <link> elements to clarify to search engines etc what the 
        # official link is
        english_version = PageContent.objects.get(slug=slug, language_id=1)
        return PageContent.objects.get(page_id=english_version.page_id, language__language_code=request.language)
    except:
        return PageContent()

@csrf_exempt
def index(request):
    context = {
        "menu": "home",
        "inspiration": Inspiration.objects.all(),
        "education": get_page(request, "education-and-outreach"),
        "research": get_page(request, "research"),
        "summary": get_page(request, "summary"),
    }

    return render(request, "index.html", context)

@csrf_exempt
def page(request, slug):
    info = get_page(request, slug)
    parent_page = PageContent.objects.get(page=info.page.parent_page, language__language_code=request.language)

    # When a page is the main page in a section, we want to show the title as 'Overview' because the name of the
    # page already appears on top of the sidebar, and it looks a bit too duplicated otherwise.
    if info == parent_page:
        info.title = _("Overview")

    title = info.title
    if info.page.parent_page:
        title += " - " + info.page.parent_page.name

    context = {
        "info": info,
        "menu": parent_page.page.slug,
        "parent_page": parent_page,
        "page": slug,
        "sidebar": PageContent.objects.filter(page__parent_page=info.page.parent_page, language__language_code=request.language, page__is_active=True),
        "canonical": info.get_absolute_url(),
        "title": title,
        "info_description": True,
    }

    return render(request, "page.html", context)

@csrf_exempt
def page_simple(request, slug):
    info = get_page(request, slug)

    title = info.title
    if info.page.parent_page:
        title += " - " + info.page.parent_page.name

    context = {
        "info": info,
        "page": slug,
        "canonical": info.get_absolute_url(),
        "title": title,
        "info_description": True,
    }

    return render(request, "page.simple.html", context)

@csrf_exempt
def templates(request):
    return render(request, "templates.html")

def contact(request):
    message_sent = False
    if request.method == "POST":
        if request.POST.get("number") == "7" and not request.POST.get("fax"):
            subject = "Untraceable University contact form"
            mailcontext = {
                "name": request.POST.get("name"),
                "email": request.POST.get("email"),
                "message": request.POST.get("message"),
            }
            msg = render_to_string("mailbody/contact.txt", mailcontext)
            email = EmailMultiAlternatives(
                subject,
                msg,
                "info@untraceable-university.org",
                ["info@untraceable-university.org"],
                reply_to=[request.POST.get("email")],
            )
            email.send()
            messages.success(request, _("Thanks, we have received your information. We will get back to you within a few days."))
            message_sent = True
        else:
            messages.error(request, _("Sorry, please enter the right value in the robot check question."))

    info = get_page(request, "contact")

    context = {
        "info": info,
        "menu": "contact",
        "message_sent": message_sent,
        "title": info.title,
    }

    return render(request, "contact.html", context)

# This is the control panel, where staff can edit information
@staff_member_required
def controlpanel(request):

    context = {
        "controlpanel": True,
        "pages": Page.objects.all(),
    }

    return render(request, "controlpanel/index.html", context)

@staff_member_required
def controlpanel_page(request, id=None):

    info = None
    if id:
        info = Page.objects.get(pk=id)

    if request.GET.get("parent"):
        initial = {"parent_page": request.GET["parent"]}
    else:
        initial = {}

    PageForm = modelform_factory(Page, fields=("name", "parent_page", "position", "format", "slug", "is_active"))
    PageContentForm = modelform_factory(PageContent, fields=("title", "content", "slug"))

    languages = Language.objects.all()
    forms = {}
    for each in languages:
        content = PageContent.objects.filter(language=each, page=info).first()
        forms[each.name] = { "language_id": each.id, "form": PageContentForm(request.POST, instance=content, prefix=each.language_code) if request.method == "POST" else PageContentForm(instance=content, prefix=each.language_code) }

    if request.method == "POST":
        form = PageForm(request.POST, instance=info)
        if form.is_valid():
            page = form.save()
            messages.success(request, "The information was saved.")
        else:
            messages.warning(request, form.errors)

        for language_name, form_data in forms.items():
            form = form_data["form"]
            form.instance.language_id = form_data["language_id"]
            form.instance.page_id = page.id
            if form.is_valid():
                form.save()
            else:
                messages.warning(request, form.errors)

        if "redirect" in request.GET:
            return redirect(request.GET["redirect"])
        else:
            return redirect(request.get_full_path())

    else:
        form = PageForm(instance=info, initial=initial)

    context = {
        "info": info,
        "controlpanel": True,
        "form": form,
        "forms": forms,
    }

    return render(request, "controlpanel/page.html", context)

