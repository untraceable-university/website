from django.db import models
from markdown import markdown
from django.utils.safestring import mark_safe
from mdeditor.fields import MDTextField
from django.utils.translation import gettext_lazy as _

def get_date_range(start, end, months_only=False):

    if start and not end and months_only:
        return "Since " + start.strftime("%b %Y")

    elif start and not end:
        return "Start date: " + start.strftime("%b %d, %Y")

    if not start or not end:
        return None

    start_date = start.strftime("%b %Y") if months_only else start.strftime("%b %d, %Y")
    start_time = "00:00" if months_only else start.strftime("%H:%M")
    end_date = end.strftime("%b %Y") if months_only else end.strftime("%b %d, %Y")
    end_time = "00:00" if months_only else end.strftime("%H:%M")

    if start_date == end_date:
        if months_only:
            return start_date
        elif start_time == "00:00" and end_time == "00:00":
            return start_date
        elif start_time == end_time:
            return start.strftime("%b %d, %Y %H:%M")
        else:
            return start_date + " " + start_time + " - " + end_time
    else:
        if start.strftime("%Y%m") == end.strftime("%Y%m"):
            return start.strftime("%b") + " " + start.strftime("%d") + " - " + end.strftime("%d") + ", " + start.strftime("%Y")
        elif start_time != "00:00" and end_time != "00:00":
            return start.strftime("%b %d, %Y %H:%M") + " - " + end.strftime("%b %d, %Y %H:%M")
        elif start.strftime("%Y") == end.strftime("%Y"):
            if months_only:
                return start.strftime("%b") + " - " + end_date
            else:
                return start.strftime("%b %d") + " - " + end_date
        else:
            return start_date + " - " + end_date


class Language(models.Model):
    name = models.CharField(max_length=255)
    language_code = models.CharField(max_length=5, help_text="Language code used in Django to pull in the right locale")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Page(models.Model):
    name = models.CharField(max_length=255)
    parent_page = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    is_active = models.BooleanField(db_index=True, default=True)
    created_at = models.DateTimeField(auto_now=True)
    FORMAT = [
        ("markdown", "Markdown"),
        ("html", "HTML"),
        ("blurb", "Blurb"),
        ("faq", "FAQ"),
    ]
    format = models.CharField(max_length=8, choices=FORMAT, db_index=True, default="markdown")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["parent_page_id", "position", "name"]

class PageContent(models.Model):
    title = models.CharField(max_length=255)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="content")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = MDTextField(null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_content(self):
        # Activate the markdown in HTML extension because we sometimes want to add a div with a specific class inside the markdown
        return mark_safe(markdown(self.content, extensions=["md_in_html"]) if self.page.format == "markdown" or self.page.format == "blurb" else self.content)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.language_id != 1:
            url = "/es/"
        else:
            url = "/"
        if self.page.parent_page:
            url += self.page.parent_page.slug + "/"
        url += self.page.slug + "/"
        return url

    class Meta:
        ordering = ["page__position", "title"]

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    related_to = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, related_name="questions")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    answer = MDTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def get_content(self):
        return mark_safe(markdown(self.content))

    def __str__(self):
        return self.question

    class Meta:
        ordering = ["created_at"]

class Inspiration(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    image = models.FileField(null=True, blank=True, upload_to="inspiration")
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["position", "title"]

class Discipline(models.Model):
    name = models.CharField(max_length=255)
    translations = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Question(models.Model):
    question = models.CharField(max_length=1000)
    research_question = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1=Take stock, 2=Barriers, 3=Integrated visions, 4=Framework")
    description = models.TextField(null=True, blank=True)
    discipline = models.ManyToManyField(Discipline)
    translations = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ["question"]

class Link(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    details = models.JSONField()
    position = models.PositiveSmallIntegerField()
    CATEGORIES = [
        ("docs", "Useful documents"),
        ("links", "Useful links"),
    ]
    category = models.CharField(max_length=8, choices=CATEGORIES, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["position"]

    @property
    def icon(self):
        try:
            return self.details["icon"]
        except:
            return None

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    notes_html = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    url = models.URLField(null=True, blank=True, max_length=1000)
    is_partner = models.BooleanField(db_index=True, default=False)
    logo = models.ImageField(null=True, blank=True, upload_to="logos")
    tags = models.ManyToManyField(Tag)

    def get_notes(self):
        if self.notes:
            return mark_safe(self.notes_html)
        else:
            return ""

    def get_description(self):
        if self.description:
            return mark_safe(markdown(self.description, extensions=["nl2br"]))
        else:
            return ""

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class People(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    notes_html = models.TextField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    url = models.URLField(null=True, blank=True, max_length=1000)
    email = models.EmailField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    @property
    def firstname(self):
        name = self.name
        return name.split(" ")[0]

    def get_notes(self):
        if self.notes:
            return mark_safe(self.notes_html)
        else:
            return ""

    def get_description(self):
        if self.description:
            return mark_safe(markdown(self.description))
        else:
            return ""

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    meeting_notes = models.TextField(blank=True, null=True)
    thirtyseconds = models.TextField(blank=True, null=True)
    directions = models.TextField(blank=True, null=True)
    people = models.ManyToManyField(People, through="EventRelationship")
    is_finished = models.BooleanField(default=False)

    EVENT_TYPES = [
        ("meeting", _("Meeting")),
    ]
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date_start", "-date_end", "name"]

    def get_description(self):
        if self.description:
            return mark_safe(markdown(self.description, extensions=["nl2br"]))
        else:
            return ""

    def get_notes(self):
        return mark_safe(markdown(self.meeting_notes, extensions=["nl2br"]))
        
    @property
    def get_dates(self):
        return get_date_range(self.date_start, self.date_end)

    @property
    def get_dates_months(self):
        return get_date_range(self.date_start, self.date_end, True)

class EventRelationship(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    RELATIONSHIPS = [
        ("participant", _("Participant")),
    ]
    relationship = models.CharField(max_length=15, choices=RELATIONSHIPS, db_index=True)
