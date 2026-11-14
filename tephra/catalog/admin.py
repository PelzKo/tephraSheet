import copy

from django import forms
from django.contrib import admin
from django.forms.models import construct_instance

from rules.lang import gettext as _

from .models import ItemTemplate


class ConfirmViolationsForm(forms.ModelForm):
    """Admin form: a save that breaks the rules isn't blocked, but needs "Save anyway" ticked. Subclasses list the
    violations of the object as it would be saved."""

    confirm_violations = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirm_violations"].label = _("Save anyway")

    def violations(self, obj):
        return obj.augment_problems  # items; house-rule items have none

    def clean(self):
        data = super().clean()
        if self.errors or data.get("confirm_violations") or (self.instance.pk and not self.has_changed()):
            return data
        found = self.violations(construct_instance(self, copy.copy(self.instance)))
        if found:
            raise forms.ValidationError(_("Do you really want to do that? {problems}. Tick “Save anyway” to save.",
                                          problems="; ".join(found)))
        return data


@admin.register(ItemTemplate)
class ItemTemplateAdmin(admin.ModelAdmin):
    form = ConfirmViolationsForm
    list_display = ["name", "kind", "size", "price_dukes", "is_starting_gear", "source"]
    list_filter = ["kind", "size", "source", "modified", "is_starting_gear", "extension"]
    search_fields = ["name", "description"]
