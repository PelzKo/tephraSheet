from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .. import access
from ..models import Character, Feedback, NarratorSettings


def character_list(request):
    unlocked = access.unlocked_ids(request)
    cards = []
    for c in Character.objects.all():
        card = {"character": c, "unlocked": c.pk in unlocked or access.is_gm(request)}
        if c.status == "active" and c.race:
            sheet = c.compute()
            weapon = sheet.weapons[0] if sheet.weapons else sheet.unarmed
            card.update(sheet=sheet, weapon=weapon,
                        hp=c.current_hp if c.current_hp is not None else sheet.max_hp,
                        wounds=c.current_wounds if c.current_wounds is not None else sheet.max_wounds)
        cards.append(card)
    return render(request, "characters/list.html", {"cards": cards})


@require_POST
def character_new(request):
    character = Character.objects.create()
    access.unlock(request, character)
    return redirect("wizard", pk=character.pk)


def unlock_view(request, pk):
    character = get_object_or_404(Character, pk=pk)
    if access.can_access(request, character):
        return redirect(character.get_absolute_url())
    error = ""
    if not character.password:
        error = "This character has no password yet. Ask the narrator to set one."
    if request.method == "POST":
        if access.is_throttled(request, character):
            error = "Too many wrong attempts. Wait a few minutes."
        elif character.check_password(request.POST.get("password", "")):
            access.clear_failures(request, character)
            access.unlock(request, character)
            return redirect(character.get_absolute_url())
        else:
            access.register_failure(request, character)
            error = "Wrong password."
    return render(request, "characters/unlock.html", {"character": character, "error": error})


@require_POST
def lock_view(request, pk):
    character = get_object_or_404(Character, pk=pk)
    access.lock(request, character)
    return redirect("character_list")


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, min_length=3, label="New password")
    confirm = forms.CharField(widget=forms.PasswordInput, label="Repeat password")

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("confirm"):
            raise forms.ValidationError("Passwords don't match.")
        return data


@access.character_view
def password_view(request, character):
    form = PasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        character.set_password(form.cleaned_data["password"])
        character.save(update_fields=["password"])
        messages.success(request, "Password changed.")
        return redirect("sheet", pk=character.pk)
    return render(request, "characters/password.html", {"character": character, "form": form})


@require_POST
@access.character_view
def delete_view(request, character):
    if not access.is_gm(request) and character.status != "draft":
        messages.error(request, "Only the narrator can delete finished characters.")
        return redirect("sheet", pk=character.pk)
    character.delete()
    messages.success(request, "Character deleted.")
    return redirect("character_list")


class GMLoginView(auth_views.LoginView):
    template_name = "characters/gm_login.html"


class SettingsForm(forms.ModelForm):
    class Meta:
        model = NarratorSettings
        fields = ["allow_choose_random_trait", "allow_reroll_random_trait", "background_story_count",
                  "max_starting_level", "allow_player_admin_mode"]


@staff_member_required(login_url="gm_login")
def gm_settings(request):
    obj = NarratorSettings.get()
    form = SettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Narrator settings saved.")
        return redirect("gm_settings")
    feedback = list(Feedback.objects.select_related("character"))
    return render(request, "characters/gm_settings.html", {
        "form": form, "characters": Character.objects.all(), "feedback": feedback,
        "feedback_open": sum(1 for f in feedback if f.is_open), "feedback_statuses": Feedback.STATUS_CHOICES})


@staff_member_required(login_url="gm_login")
@require_POST
def gm_reset_password(request, pk):
    character = get_object_or_404(Character, pk=pk)
    raw = request.POST.get("password", "")
    if len(raw) < 3:
        messages.error(request, "Password must have at least 3 characters.")
    else:
        character.set_password(raw)
        character.save(update_fields=["password"])
        messages.success(request, f"Password of {character} reset.")
    return redirect("gm_settings")
