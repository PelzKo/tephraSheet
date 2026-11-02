from django.db import models
from django.urls import reverse


class WikiPage(models.Model):
    """A page anyone can write (house rules, lore, tips). ``language`` empty = shown in every language."""

    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True, help_text="Markdown")
    language = models.CharField(max_length=10, blank=True)
    updated_by = models.CharField(max_length=80, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("wiki_page", args=[self.slug])


class WikiRevision(models.Model):
    """The previous version of a page, saved on every edit (restore in the Django admin)."""

    page = models.ForeignKey(WikiPage, on_delete=models.CASCADE, related_name="revisions")
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    edited_by = models.CharField(max_length=80, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
