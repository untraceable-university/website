from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth import logout

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
from django.utils import timezone

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
        file_path = os.path.join(settings.MEDIA_ROOT, "leads.json")
        with open(file_path, "r") as json_file:
            j = json.load(json_file)
            for each in j:
                info = Lead.objects.create(
                    name=each["name"],
                    url=each["url"],
                    description=each["description"],
                    notes=each["notes"],
                    created_at=each["created_at"],
                )
                for tag in each["tags"]:
                    if tag != "Untraceable University":
                        tag, created = Tag.objects.get_or_create(name=tag)
                        info.tags.add(tag)



    context = {
        "controlpanel": True,
        "pages": Page.objects.all(),
        "menu": "index",
        "links": Link.objects.filter(category="links"),
        "docs": Link.objects.filter(category="docs"),
        "events": Event.objects.filter(date_end__gte=timezone.now()).order_by("date_start")[:5],
        "past_events": Event.objects.filter(date_end__lt=timezone.now()).order_by("-date_start")[:5],
        "leads": Lead.objects.all().order_by("-created_at")[:5],
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
        "people": People.objects.filter(tags=info),
        "leads": Lead.objects.filter(tags=info),
        "info": info,
    }

    return render(request, "controlpanel/tagged.html", context)

@staff_member_required
def controlpanel_organizations(request):

    context = {
        "controlpanel": True,
        "organizations": Organization.objects.all(),
        "menu": "contacts",
        "page": "organizations",
        "load_datatables": True,
        "datatables_order": 1,
    }

    return render(request, "controlpanel/organizations.html", context)

@staff_member_required
def controlpanel_organization_form(request, id=None):

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
            return redirect(reverse("controlpanel_organization", args=[info.id]))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "organizations",
        "countries": Country.objects.all(),
    }

    return render(request, "controlpanel/organization.form.html", context)

@staff_member_required
def controlpanel_organization(request, id):

    info = Organization.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "organizations",
        "tags": Tag.objects.all(),
    }

    return render(request, "controlpanel/organization.html", context)

@staff_member_required
def controlpanel_people_list(request):

    if "import" in request.GET:
        file_path = os.path.join(settings.MEDIA_ROOT, "people.json")
        with open(file_path, "r") as json_file:
            j = json.load(json_file)
            for each in j:
                info = People.objects.create(
                    name=each["name"],
                    email=each["email"],
                    phone=each["phone"],
                    url=each["url"],
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
        "people": People.objects.all(),
        "menu": "contacts",
        "page": "people",
        "load_datatables": True,
    }

    return render(request, "controlpanel/people.html", context)

@staff_member_required
def controlpanel_people(request, id):

    info = People.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "people",
        "tags": Tag.objects.all(),
        "engagements": Event.objects.filter(people=info),
    }

    return render(request, "controlpanel/person.html", context)

@staff_member_required
def controlpanel_people_form(request, id=None):

    info = People()
    if id:
        info = People.objects.get(pk=id)
        
    if request.method == "POST":
        info.name = request.POST["name"]
        info.email = request.POST["email"]
        info.phone = request.POST["phone"]
        info.url = request.POST["url"]
        info.description = request.POST["description"]
        info.country_id = request.POST.get("country")
        info.save()
        messages.success(request, _("Information was saved."))
        return redirect(reverse("controlpanel_people_list"))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "people",
        "tags": Tag.objects.all(),
        "countries": Country.objects.all(),
    }

    return render(request, "controlpanel/person.form.html", context)

@staff_member_required
def controlpanel_events(request, event_type="meetings"):

    if "import" in request.GET:
        Event.objects.all().delete()
        file_path = os.path.join(settings.MEDIA_ROOT, "meetings.json")
        with open(file_path, "r") as json_file:
            j = json.load(json_file)
            for each in j:
                info = Event.objects.create(
                    name=each["name"],
                    description=each["description"],
                    meeting_notes=each["notes"] if each["notes"] else each["meeting_notes"],
                    thirtyseconds=each["thirtyseconds"],
                    date_start=each["scheduled_date_start"],
                    date_end=each["scheduled_date_end"],
                    is_finished=each["finished"],
                    directions=each["directions"],
                    event_type="meeting",
                )
                for people in each["people"]:
                    people = People.objects.get(name=people)
                    EventRelationship.objects.create(event=info, people=people, relationship="participant")

    events = Event.objects.all()
    if event_type:
        events = events.filter(event_type=event_type)

    events = events.prefetch_related("people")
    show_summaries = False

    if "upcoming" in request.GET:
        events = events.filter(date_end__gte=timezone.now())
    elif not "all" in request.GET:
        show_summaries = True
        events = events.filter(date_end__lte=timezone.now())

    context = {
        "controlpanel": True,
        "events": events,
        "menu": "contacts",
        "page": event_type,
        "load_datatables": True,
        "datatables_order": 1,
        "show_summaries": show_summaries,
    }

    return render(request, "controlpanel/events.html", context)


@staff_member_required
def controlpanel_event(request, id):

    info = Event.objects.get(pk=id)
    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "meeting",
        "all_people": People.objects.all(),
    }

    return render(request, "controlpanel/event.html", context)

@staff_member_required
def controlpanel_event_form(request, id=None):

    info = Event()
    if id:
        info = Event.objects.get(pk=id)
        
    if request.method == "POST":
        info.name = request.POST["name"]
        info.description = request.POST["description"]
        info.meeting_notes = request.POST["meeting_notes"]
        info.thirtyseconds = request.POST["thirtyseconds"]
        info.directions = request.POST["directions"]
        info.event_type = request.POST["event_type"]

        date_start = request.POST.get("date_start")
        time_start = request.POST.get("time_start")
        info.date_start = f"{date_start} {time_start}"

        date_end = request.POST.get("date_end")
        time_end = request.POST.get("time_end")
        info.date_end = f"{date_end} {time_end}"

        info.save()
        messages.success(request, _("Information was saved."))
        if "redirect" in request.GET:
            return redirect(request.GET["redirect"])
        else:
            return redirect(reverse("controlpanel_meeting", args=[info.id]))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "contacts",
        "page": "people",
        "tags": Tag.objects.all(),
        "event_types": Event.EVENT_TYPES,
    }

    return render(request, "controlpanel/event.form.html", context)

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

@staff_member_required
def controlpanel_leads(request):

    context = {
        "controlpanel": True,
        "leads": Lead.objects.all(),
        "menu": "leads",
        "page": "leads",
        "load_datatables": True,
    }

    return render(request, "controlpanel/leads.html", context)

@staff_member_required
def controlpanel_lead(request, id):

    info = Lead.objects.get(pk=id)

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "leads",
        "page": "leads",
        "tags": Tag.objects.all(),
    }

    return render(request, "controlpanel/lead.html", context)

@staff_member_required
def controlpanel_lead_form(request, id=None):

    info = Lead()
    if id:
        info = Lead.objects.get(pk=id)

    if request.method == "POST":
        info.name = request.POST["name"]
        info.description = request.POST["description"]
        info.notes = request.POST["notes"]
        info.url = request.POST["url"]
        info.created_at = timezone.now()
        info.save()

        messages.success(request, _("Information was saved."))

        return redirect(reverse("controlpanel_lead", args=[info.id]))

    context = {
        "controlpanel": True,
        "info": info,
        "menu": "leads",
        "page": "lead_form",
    }

    return render(request, "controlpanel/lead.form.html", context)

@staff_member_required
def controlpanel_profile(request):

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST["first_name"]
        user.last_name = request.POST["last_name"]
        user.email = request.POST["email"]
        user.username = request.POST["email"]

        if request.POST.get("password"):
            user.set_password(request.POST["password"])

        user.save()


    context = {
        "controlpanel": True,
        "menu": "profile",
        "page": "profile",
    }

    return render(request, "controlpanel/profile.html", context)

def controlpanel_logout(request):
    logout(request)
    messages.success(request, _("You are now logged out."))
    return redirect("/")

@csrf_exempt
def controlpanel_ajax_tags(request):
    if request.method == "DELETE":
        page = request.GET["page"]
        tag = Tag.objects.get(pk=request.GET["tag"])
        if page == "people":
            info = People.objects.get(pk=request.GET["id"])
        elif page == "leads":
            info = Lead.objects.get(pk=request.GET["id"])
        elif page == "organizations":
            info = Organization.objects.get(pk=request.GET["id"])
        info.tags.remove(tag)
        return JsonResponse({"response":"OK"}, safe=False)
    elif request.method == "POST":
        tag = Tag.objects.get(pk=request.POST["tag"])
        page = request.POST["page"]
        if page == "people":
            info = People.objects.get(pk=request.POST["id"])
        elif page == "leads":
            info = Lead.objects.get(pk=request.POST["id"])
        elif page == "organizations":
            info = Organization.objects.get(pk=request.POST["id"])
        info.tags.add(tag)
        d = model_to_dict(tag)
        d["response"] = "OK"
        return JsonResponse(d, safe=False)

@csrf_exempt
def controlpanel_ajax_event(request, id):
    info = Event.objects.get(pk=id)
    if request.method == "DELETE":
        people = People.objects.get(pk=request.GET["remove_participant"])
        info.people.remove(people)
        return JsonResponse({"response":"OK"}, safe=False)
    elif request.method == "POST":
        people = People.objects.get(pk=request.POST["participant"])
        info.people.add(people)
        d = {"name": people.name, "id": people.id}
        d["response"] = "OK"
        return JsonResponse(d, safe=False)
