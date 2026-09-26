from django.contrib import admin

from .models import Character, CustomModifier, EffectEntry, InventoryItem, LevelLog, NarratorSettings


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
