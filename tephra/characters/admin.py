from django.contrib import admin

from catalog.admin import ConfirmViolationsForm

from . import services
from .models import (Character, CustomModifier, EffectEntry, Feedback, InventoryItem, JournalRevision, LevelLog,
                     NarratorSettings)


class InventoryInline(admin.TabularInline):
    model = InventoryItem
    form = ConfirmViolationsForm
    extra = 0
    fields = ["name", "kind", "size", "slot", "quantity", "confirm_violations"]


class EffectInline(admin.TabularInline):
    model = EffectEntry
    extra = 0


class ModifierInline(admin.TabularInline):
    model = CustomModifier
    extra = 0


class CharacterForm(ConfirmViolationsForm):
    def violations(self, obj):
        return services.rule_violations(obj)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    form = CharacterForm
    list_display = ["name", "player_name", "race", "level", "status", "updated"]
    list_filter = ["status", "race"]
    search_fields = ["name", "player_name"]
    exclude = ["password"]
    inlines = [InventoryInline, EffectInline, ModifierInline]


@admin.register(JournalRevision)
class JournalRevisionAdmin(admin.ModelAdmin):
    """Earlier journal texts; "Restore" puts the chosen text back (the current text becomes a revision)."""

    list_display = ["character", "created", "preview"]
    list_filter = ["character"]
    readonly_fields = ["character", "text", "created"]
    actions = ["restore"]

    @admin.display(description="Text")
    def preview(self, obj):
        return obj.text[:80]

    @admin.action(description="Restore this journal text")
    def restore(self, request, queryset):
        for rev in queryset.order_by("character", "-created").distinct():
            character = rev.character
            JournalRevision.record(character, character.story_notes)
            character.story_notes = rev.text
            character.save(update_fields=["story_notes", "updated"])
        self.message_user(request, f"Restored {queryset.count()} journal text(s).")


admin.site.register(NarratorSettings)
admin.site.register(LevelLog)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["created", "category", "status", "name", "character_name", "page_title"]
    list_filter = ["status", "category"]
    search_fields = ["message", "name", "character_name", "page_url"]
