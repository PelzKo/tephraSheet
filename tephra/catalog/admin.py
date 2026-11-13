from django.contrib import admin

from .models import ItemTemplate


@admin.register(ItemTemplate)
class ItemTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "kind", "size", "price_dukes", "is_starting_gear", "source"]
    list_filter = ["kind", "size", "source", "modified", "is_starting_gear", "extension"]
    search_fields = ["name", "description"]
