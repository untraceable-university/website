from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=255)
    language_code = models.CharField(max_length=5, help_text="Language code used in Django to pull in the right locale")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Page(models.Model):
    name = models.CharField(max_length=255)
    FORMAT = [
        ("markdown", "Markdown"),
        ("html", "HTML"),
    ]
    format = models.CharField(max_length=8, choices=FORMAT, db_index=True, default="markdown")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class PageContent(models.Model):
    title = models.CharField(max_length=255)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="content")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

    def get_content(self):
        description = markdown(self.description) if self.page.format == "markdown" else self.description
        return mark_safe(description)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]

