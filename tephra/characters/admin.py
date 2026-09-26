from django.contrib import admin

from .models import Character, CustomModifier, EffectEntry, Feedback, InventoryItem, LevelLog, NarratorSettings


class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    fields = ["name", "kind", "size", "slot", "quantity"]


class EffectInline(admin.TabularInline):
    model = EffectEntry
    extra = 0


class ModifierInline(admin.TabularInline):
    model = CustomModifier
    extra = 0


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["name", "player_name", "race", "level", "status", "updated"]
    list_filter = ["status", "race"]
    search_fields = ["name", "player_name"]
    exclude = ["password"]
    inlines = [InventoryInline, EffectInline, ModifierInline]


admin.site.register(NarratorSettings)
admin.site.register(LevelLog)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["created", "category", "status", "name", "character_name", "page_title"]
    list_filter = ["status", "category"]
    search_fields = ["message", "name", "character_name", "page_url"]
