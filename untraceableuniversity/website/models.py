from django.db import models
from markdown import markdown
from django.utils.safestring import mark_safe
from mdeditor.fields import MDTextField

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
