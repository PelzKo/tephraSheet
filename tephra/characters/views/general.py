import functools
import subprocess
from datetime import datetime, timezone

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.db import connection
from django.utils import timezone as dj_timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from rules.extensions import EXTENSIONS
from rules.lang import get_language, gettext as _
from rules.registry import get_registry
from .. import access, actionlog
from ..middleware import remember_pass
from . import trash as trash_views
from .feedback import mail_configured
from ..models import Character, Feedback, NarratorSettings, card_cache_key

CARD_TTL = 600  # rows changed with queryset.update() skip the save signal; this bounds the staleness


def card_values(character):
    """The few numbers a front-page card shows, cached until the character (or one of its rows) changes."""
    key = card_cache_key(character.pk, get_language())
    values = cache.get(key)
    if values is None:
        sheet = character.compute()
        weapon = sheet.weapons[0] if sheet.weapons else sheet.unarmed
        stats = {k: sheet.stats[k].total for k in ("ap", "eva", "def", "pri", "spd")}
        values = {"max_hp": sheet.max_hp, "max_wounds": sheet.max_wounds, "stats": stats,
                  "weapon": {"name": weapon.name, "acc": weapon.acc.total, "dc": weapon.dc.total,
                             "stk": weapon.stk.total if weapon.stk else None}}
        cache.set(key, values, CARD_TTL)
    return values


def character_list(request):
    unlocked = access.unlocked_ids(request)
    cards = []
    for c in Character.objects.all():
        card = {"character": c, "unlocked": c.pk in unlocked or access.is_gm(request)}
        if c.status == "active" and c.race:
            values = card_values(c)
            card.update(values, hp=c.current_hp if c.current_hp is not None else values["max_hp"],
                        wounds=c.wounds_taken)
        cards.append(card)
    return render(request, "characters/list.html", {"cards": cards})


def passphrase_view(request):
    narrator_settings = NarratorSettings.get()
    target = request.POST.get("next") or request.GET.get("next") or "/"
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                           require_https=request.is_secure()):
        target = "/"
    if not narrator_settings.passphrase:
        return redirect(target)
    error = ""
    if request.method == "POST":
        key = f"pass-fail:{access.client_ip(request)}"
        if access.is_limited(key, settings.LOGIN_MAX_ATTEMPTS):
            error = _("Too many wrong attempts. Wait a few minutes.")
        elif check_password(request.POST.get("passphrase", ""), narrator_settings.passphrase):
            response = redirect(target)
            remember_pass(response, narrator_settings)
            return response
        else:
            access.hit(key)
            access.security_log.warning("wrong group passphrase from %s", access.client_ip(request))
            error = _("Wrong passphrase.")
    return render(request, "characters/passphrase.html", {"error": error, "next": target})


@require_POST
def lock_all(request):
    access.lock_all(request)
    messages.success(request, _("All characters on this device are locked again."))
    return redirect("character_list")


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
        error = _("This character has no password yet. Ask the narrator to set one.")
    if request.method == "POST":
        if access.is_throttled(request, character):
            error = _("Too many wrong attempts. Wait a few minutes.")
        elif character.check_password(request.POST.get("password", "")):
            access.clear_failures(request, character)
            access.unlock(request, character)
            actionlog.log(request, "unlock", character)
            return redirect(character.get_absolute_url())
        else:
            access.register_failure(request, character)
            actionlog.log(request, "unlock:failed", character)
            error = _("Wrong password.")
    return render(request, "characters/unlock.html", {"character": character, "error": error})


@require_POST
def lock_view(request, pk):
    character = get_object_or_404(Character, pk=pk)
    access.lock(request, character)
    return redirect("character_list")


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, min_length=access.MIN_PASSWORD)
    confirm = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].label = _("New password")
        self.fields["confirm"].label = _("Repeat password")

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("confirm"):
            raise forms.ValidationError(_("Passwords don't match."))
        return data


@access.character_view
def password_view(request, character):
    form = PasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        character.set_password(form.cleaned_data["password"])
        character.save(update_fields=["password"])
        access.unlock(request, character)  # keep this session, revoke all others
        actionlog.log(request, "password", character)
        messages.success(request, _("Password changed."))
        return redirect("sheet", pk=character.pk)
    return render(request, "characters/password.html", {"character": character, "form": form})


@require_POST
@access.character_view
def delete_view(request, character):
    if not access.is_gm(request) and character.status != "draft":
        messages.error(request, _("Only the narrator can delete finished characters."))
        return redirect("sheet", pk=character.pk)
    actionlog.log(request, "delete", character)
    character.deleted_at = dj_timezone.now()
    character.save(update_fields=["deleted_at"])
    messages.success(request, _("Character moved to the trash. The narrator can restore it on the narrator page."))
    return redirect("character_list")


class GMLoginView(auth_views.LoginView):
    """Narrator login; also serves the Django admin's login URL so both are throttled."""

    template_name = "characters/gm_login.html"

    def _key(self):
        return f"login-fail:{access.client_ip(self.request)}"

    def post(self, request, *args, **kwargs):
        if access.is_limited(self._key(), settings.LOGIN_MAX_ATTEMPTS):
            return self.render_to_response(self.get_context_data(
                form=self.form_class(request), error=_("Too many wrong attempts. Wait a few minutes.")))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        access.hit(self._key())
        access.security_log.warning("failed narrator login for %r from %s",
                                    form.data.get("username", "")[:80], access.client_ip(self.request))
        return super().form_invalid(form)


class SettingsForm(forms.ModelForm):
    enabled_extensions = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    disabled_races = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    new_passphrase = forms.CharField(required=False, min_length=access.MIN_PASSWORD,
                                     widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    remove_passphrase = forms.BooleanField(required=False)

    class Meta:
        model = NarratorSettings
        fields = ["allow_choose_random_trait", "allow_reroll_random_trait", "background_story_count",
                  "max_starting_level", "allow_player_admin_mode", "enabled_extensions", "disabled_races",
                  "feedback_email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ext, races = self.fields["enabled_extensions"], self.fields["disabled_races"]
        ext.label, races.label = _("Extensions"), _("Disabled races")
        ext.help_text = _("Switched-on extensions are offered for new choices. Characters keep what they already have.")
        races.help_text = _("Not offered when creating a new character. Existing characters keep their race.")
        ext.choices = [(k, _(name)) for k, name in EXTENSIONS.items()]
        races.choices = sorted(((r["slug"], r["name"]) for r in get_registry().races.values()), key=lambda c: c[1])
        new, remove = self.fields["new_passphrase"], self.fields["remove_passphrase"]
        new.label, remove.label = _("New group passphrase"), _("Remove the group passphrase")
        new.help_text = (_("A passphrase is set. A new one makes every browser enter it again.")
                         if self.instance.passphrase else
                         _("No passphrase set: anyone who finds the site can open it."))
        new.help_text += " " + _("Narrators never need it.")
        mail = self.fields["feedback_email"]
        mail.label = _("Email for new feedback")
        mail.help_text = (_("Each new feedback message is sent to this address.") if mail_configured()
                          else _("The server has no mail settings (EMAIL_HOST), so no mail is sent."))

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.cleaned_data.get("remove_passphrase"):
            obj.passphrase = ""
        elif self.cleaned_data.get("new_passphrase"):
            obj.passphrase = make_password(self.cleaned_data["new_passphrase"])
        obj.save()
        return obj


@functools.cache
def app_version():
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%h (%cs)"], cwd=settings.BASE_DIR,
                             capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    return out or "unknown"


def last_backup():
    try:
        newest = max((f.stat().st_mtime for f in settings.BACKUP_DIR.glob("tephra-*.gz")), default=None)
    except OSError:
        newest = None
    return newest and datetime.fromtimestamp(newest, tz=timezone.utc)


def server_info():
    return {"version": app_version(), "backup_dir": settings.BACKUP_DIR, "last_backup": last_backup(),
            "database": f"{connection.display_name} {'.'.join(map(str, connection.get_database_version()))}"}


@staff_member_required(login_url="gm_login")
def gm_settings(request):
    obj = NarratorSettings.get()
    before = actionlog.values(obj)  # before the form: is_valid() already writes into obj
    form = SettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        after = actionlog.values(obj)
        if before["passphrase"] != after["passphrase"]:  # never the hash itself
            before["passphrase"], after["passphrase"] = bool(before["passphrase"]), "changed" if after["passphrase"] else False
        actionlog.log(request, "settings", obj, before, after)
        messages.success(request, _("Narrator settings saved."))
        return redirect("gm_settings")
    feedback = list(Feedback.objects.select_related("character"))
    return render(request, "characters/gm_settings.html", {
        "form": form, "characters": Character.objects.all(), "feedback": feedback,
        "feedback_open": sum(1 for f in feedback if f.is_open), "feedback_statuses": Feedback.STATUS_CHOICES,
        "server": server_info(), **trash_views.gm_context()})


@staff_member_required(login_url="gm_login")
@require_POST
def gm_reset_password(request, pk):
    character = get_object_or_404(Character, pk=pk)
    raw = request.POST.get("password", "")
    if len(raw) < access.MIN_PASSWORD:
        messages.error(request, _("Password must have at least {n} characters.", n=access.MIN_PASSWORD))
    else:
        character.set_password(raw)
        character.save(update_fields=["password"])
        actionlog.log(request, "password", character)
        messages.success(request, _("Password of {character} reset.", character=character))
    return redirect("gm_settings")


@require_POST
def set_language(request):
    from rules.lang import languages

    from ..middleware import COOKIE

    code = request.POST.get("language", "")
    target = request.POST.get("next") or "/"
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        target = "/"
    response = redirect(target)
    if code in languages():
        request.session[COOKIE] = code
        response.set_cookie(COOKIE, code, max_age=365 * 24 * 3600, samesite="Lax")
    return response
