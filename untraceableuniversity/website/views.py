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
from django.urls import reverse

import os
import json

# Quick debugging, sometimes it's tricky to locate the PRINT in all the Django
# output in the console, so just using a simply function to highlight it better
def p(text):
    print("----------------------")
    print(text)
    print("----------------------")

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
def page(request, slug, child_page=None):
    info = get_page(request, slug)
    parent_page = PageContent.objects.get(page=info.page.parent_page, language__language_code=request.language)

    # When a page is the main page in a section, we want to show the title as 'Overview' because the name of the
    # page already appears on top of the sidebar, and it looks a bit too duplicated otherwise.
    if info == parent_page:
        info.title = _("Overview")

    title = info.title
    if info.page.parent_page:
        title += " - " + info.page.parent_page.name

    children = None
    include_file = None
    show_date = False
    if child_page:
        # Child page means that we are in a sub-sub page, such as About > News > Specific News Item. 
        # We then load a new get_page request, but only here because we do want the regular sidebar menu
        # so in this way we only overwrite the main content
        info = get_page(request, child_page)
        show_date = True
    elif info.page.slug == "news":
        children = PageContent.objects.filter(page__parent_page=info.page, language__language_code=request.language)
        include_file = "_news.html"

    context = {
        "info": info,
        "menu": parent_page.page.slug,
        "parent_page": parent_page,
        "page": slug,
        "sidebar": PageContent.objects.filter(page__parent_page=parent_page.page, language__language_code=request.language, page__is_active=True),
        "canonical": info.get_absolute_url(),
        "title": title,
        "info_description": True,
        "children": children,
        "include_file": include_file,
        "show_date": show_date,
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

def video(request):
    return render(request, "video.html")

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
        "hide_partners": True,
    }

    return render(request, "contact.html", context)

# This is the control panel, where staff can edit information
# STAFF ONLY for all pages
@staff_member_required
def controlpanel(request):

    if "import" in request.GET:
        import csv
        with open('media/import/countries.csv', mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                Country.objects.create(id=row[0], name=row[1])


    context = {
        "controlpanel": True,
        "pages": Page.objects.all(),
        "menu": "index",
        "links": Link.objects.filter(category="links"),
        "docs": Link.objects.filter(category="docs"),
    }

    return render(request, "controlpanel/index.html", context)

@staff_member_required
def controlpanel_pages(request):

    context = {
        "controlpanel": True,
        "pages": Page.objects.all(),
        "menu": "content",
        "page": "pages",
    }

    return render(request, "controlpanel/pages.html", context)

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
        "menu": "content",
    }

    return render(request, "controlpanel/page.html", context)

@staff_member_required
def controlpanel_tags(request):

    context = {
        "controlpanel": True,
        "tags": Tag.objects.all(),
        "menu": "contacts",
        "page": "tags",
    }

    return render(request, "controlpanel/tags.html", context)

@staff_member_required
def controlpanel_tag(request, id=None):

    info = Tag()
    if id:
        info = Tag.objects.get(pk=id)

    if request.method == "POST":
        info.name = request.POST["name"]
        info.save()

        messages.success(request, _("Information was saved."))
        return redirect(reverse("controlpanel_tags"))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "tags",
    }

    return render(request, "controlpanel/tag.html", context)

@staff_member_required
def controlpanel_tagged(request, id):

    info = Tag.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "menu": "contacts",
        "page": "tags",
        "organizations": Organization.objects.filter(tags=info),
        "info": info,
    }

    return render(request, "controlpanel/tagged.html", context)

@staff_member_required
def controlpanel_organizations(request):

    if "import" in request.GET:
        file_path = os.path.join(settings.MEDIA_ROOT, "organizations.json")
        with open(file_path, "r") as json_file:
            j = json.load(json_file)
            for each in j:
                info = Organization.objects.create(
                    name=each["name"],
                    country_id=each["country"],
                    description=each["description"],
                    notes=each["notes"],
                    notes_html=each["notes_html"],
                )
                for tag in each["tags"]:
                    if tag != "Untraceable University":
                        tag, created = Tag.objects.get_or_create(name=tag)
                        info.tags.add(tag)

    context = {
        "controlpanel": True,
        "organizations": Organization.objects.all(),
        "menu": "contacts",
        "page": "organizations",
        "load_datatables": True,
    }

    return render(request, "controlpanel/organizations.html", context)

@staff_member_required
def controlpanel_organization(request, id=None):

    info = Organization()
    if id:
        info = Organization.objects.get(pk=id)

    if request.method == "POST":
        info.name = request.POST["name"]
        info.description = request.POST["description"]
        info.url = request.POST["url"]
        info.country_id = request.POST.get("country")
        info.is_partner = True if request.POST.get("is_partner") else False
        if "logo" in request.FILES:
            info.logo = request.FILES["logo"]
        info.save()

        messages.success(request, _("Information was saved."))

        if "redirect" in request.GET:
            return redirect(request.GET["redirect"])
        else:
            return redirect(reverse("controlpanel_organizations"))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "organizations",
        "countries": Country.objects.all(),
    }

    return render(request, "controlpanel/organization.html", context)

@staff_member_required
def controlpanel_people_list(request):

    context = {
        "controlpanel": True,
        "people": People.objects.all(),
        "menu": "contacts",
        "page": "people",
    }

    return render(request, "controlpanel/people.html", context)

@staff_member_required
def controlpanel_people(request, id=None):

    info = None
    if id:
        info = People.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "people",
    }

    return render(request, "controlpanel/people.html", context)

@staff_member_required
def controlpanel_events(request, event_type="meetings"):

    events = Event.objects.all()
    if event_type:
        events = events.filter(event_type=event_type)

    context = {
        "controlpanel": True,
        "eventes": events,
        "menu": "events",
        "page": "events",
    }

    return render(request, "controlpanel/events.html", context)


@staff_member_required
def controlpanel_event(request, id=None):

    info = None
    if id:
        info = Event.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "events",
        "page": "event",
    }

    return render(request, "controlpanel/event.html", context)

@staff_member_required
def controlpanel_links(request):

    context = {
        "controlpanel": True,
        "links": Link.objects.all().order_by("category", "position"),
        "menu": "links",
        "page": "links",
    }

    return render(request, "controlpanel/links.html", context)

@staff_member_required
def controlpanel_link(request, id=None):

    info = None
    if id:
        info = Link.objects.get(pk=id)

    if request.method == "POST":
        if not info:
            info = Link()
        info.name = request.POST["name"]
        info.description = request.POST.get("description")
        info.category = request.POST["category"]
        info.position = request.POST["position"]
        info.details = {}
        post = ["link_view_en", "link_view_es", "link_edit_en", "link_edit_es", "icon"]
        for each in post:
            if request.POST.get(each):
                info.details[each] = request.POST.get(each)
            else:
                info.details.pop(each, None)
        info.save()
        messages.success(request, _("Information was saved."))
        return redirect(reverse("controlpanel_links"))

    icons = ["file-pdf", "file-earmark-easel", "file-spreadsheet", "card-list"]

    details = {}
    if info and info.details:
        for key,value in info.details.items():
            details[key] = value

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "links",
        "page": "edit" if info else "add",
        "categories": Link.CATEGORIES,
        "icons": icons,
        "details": details,
    }

    return render(request, "controlpanel/link.html", context)
