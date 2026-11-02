from django.contrib import admin

from .models import WikiPage, WikiRevision


class RevisionInline(admin.TabularInline):
    model = WikiRevision
    extra = 0
    readonly_fields = ["title", "body", "edited_by", "created"]


@admin.register(WikiPage)
class WikiPageAdmin(admin.ModelAdmin):
    list_display = ["title", "language", "updated_by", "updated"]
    search_fields = ["title", "body"]
    inlines = [RevisionInline]
