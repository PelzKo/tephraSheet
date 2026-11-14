"""Character export/import as JSON (S4), also used to duplicate a character (C14) and for level-up snapshots.

The file is a trust boundary: only known keys, every field goes through the model field's ``to_python`` and
``full_clean``, rule slugs must exist in the registry, and the result must compute. Imports always create a
NEW character with a new password; nothing is ever overwritten.
"""
import json

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.utils import timezone

from rules.engine.pets import compute_pet
from rules.lang import gettext as _
from rules.registry import get_registry
from . import access
from .journal import level_history
from .models import Automaton, Character, CustomModifier, EffectEntry, InventoryItem, LevelLog, Pet

FORMAT, VERSION = "tephra-character", 1
MAX_BYTES = 2_000_000
CHARACTER_SKIP = {"id", "password", "created", "updated", "deleted_at", "portrait"}
CHILDREN = {  # export key: (model, fields not in the file)
    "items": (InventoryItem, {"id", "character", "template"}),
    "effects": (EffectEntry, {"id", "character"}),
    "custom_modifiers": (CustomModifier, {"id", "character"}),
    "level_logs": (LevelLog, {"id", "character"}),
    "pets": (Pet, {"id", "character"}),
    "automatons": (Automaton, {"id", "character", "weapon", "armor"}),
}
TOP_KEYS = {"format", "version", "exported", "character", *CHILDREN}
ID_KEYS = {"items": "item", "custom_modifiers": "custom"}  # children whose pk appears in toggle keys ("item:<pk>…")


def _strs(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _str_map(v, value_types):
    return isinstance(v, dict) and all(isinstance(k, str) and isinstance(x, value_types) and not isinstance(x, bool) for k, x in v.items())


def _plan_entry(e):
    return (isinstance(e, dict) and type(e.get("level")) is int and _str_map(e.get("skills") or {}, int)
            and isinstance(e.get("specialty", ""), str) and _strs(e.get("augments", []))
            and _strs(e.get("retrofit") or []) and isinstance(e.get("note", ""), str))


FIGHT_TYPES = {"active": bool, "my_turn": bool, "upkeep_choice": bool, "ap": int, "round": int}
CHARACTER_SHAPES = {  # member types of Character JSON fields (the container type is checked for every JSONField)
    "fixed_traits": _strs, "random_traits": _strs, "augments": _strs, "stories": _strs, "toggles": _strs,
    "narrator_granted": _strs,
    "skills": lambda v: _str_map(v, int), "misc": lambda v: _str_map(v, int),
    "specialty_choices": lambda v: _str_map(v, str), "trait_choices": lambda v: all(isinstance(k, str) for k in v),
    "specialties": lambda v: all(isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and type(x[1]) is int
                                 for x in v),
    "body_augments": lambda v: all(isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and type(x[1]) is int
                                   for x in v),
    "fight": lambda v: all(k in FIGHT_TYPES and type(x) is FIGHT_TYPES[k] for k, x in v.items()),
    "plan": lambda v: all(map(_plan_entry, v)),
}


class TransferError(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


def _fields(model, skip):
    return {f.name: f for f in model._meta.concrete_fields if f.name not in skip}


def _dump(obj, skip):
    return {name: f.value_from_object(obj) for name, f in _fields(type(obj), skip).items()}


def export_character(character):
    """Everything about a character as JSON-safe data (no password)."""
    items = list(character.items.all())
    index = {i.pk: n for n, i in enumerate(items)}
    data = {"format": FORMAT, "version": VERSION, "exported": timezone.now(),
            "character": _dump(character, CHARACTER_SKIP), "items": [_dump(i, CHILDREN["items"][1]) for i in items]}
    for key in ("effects", "custom_modifiers", "level_logs", "pets"):
        data[key] = [_dump(o, CHILDREN[key][1]) for o in getattr(character, key).all()]
    for key in ID_KEYS:  # file-local ids, so import can rewrite toggle keys to the new pks
        for row, obj in zip(data[key], getattr(character, key).all() if key != "items" else items):
            row["id"] = obj.pk
    data["automatons"] = [dict(_dump(a, CHILDREN["automatons"][1]), weapon=index.get(a.weapon_id),
                               armor=index.get(a.armor_id)) for a in character.automatons.all()]
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def parse_upload(upload):
    """The uploaded file as data; TransferError if it is too big or no JSON object."""
    if upload is None:
        raise TransferError([_("Choose a file.")])
    if upload.size > MAX_BYTES:
        raise TransferError([_("The file is too big (at most {n} MB).", n=MAX_BYTES // 1_000_000)])
    try:
        return json.loads(upload.read().decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        raise TransferError([_("The file is not valid JSON.")]) from None


def _build(model, row, skip, label, errors, extra=()):
    """An unsaved model instance from one row of the file; problems go to ``errors``."""
    if not isinstance(row, dict):
        errors.append(_("{label}: not an object.", label=label))
        return None
    fields = _fields(model, skip)
    unknown = set(row) - set(fields) - set(extra)
    if unknown:
        errors.append(_("{label}: unknown fields {names}.", label=label, names=", ".join(sorted(map(str, unknown)))))
        return None
    obj = model()
    for name, value in row.items():
        if name in fields:
            try:
                setattr(obj, fields[name].attname, fields[name].to_python(value))
            except (ValidationError, TypeError, ValueError):
                errors.append(_("{label}: invalid value for {name}.", label=label, name=name))
                continue
            # JSONField only checks serializability: the value must have the default's container type (list/dict)
            shape = CHARACTER_SHAPES.get(name) if model is Character else None
            if isinstance(fields[name], models.JSONField) and callable(fields[name].default) and (
                    type(value) is not type(fields[name].default()) or shape and not shape(value)):
                errors.append(_("{label}: invalid value for {name}.", label=label, name=name))
        elif name == "id" and type(value) is not int:
            errors.append(_("{label}: invalid value for {name}.", label=label, name=name))
    try:
        obj.full_clean(exclude=["character", "template", "weapon", "armor"], validate_unique=False)
    except ValidationError as e:
        errors.extend(f"{label}: {k}: {' '.join(v)}" for k, v in e.message_dict.items())
    return obj


def _unknown_slugs(c, items):
    """Rule slugs the registry does not know: ["Specialty: foo", …]."""
    reg = get_registry()
    out = []

    def check(label, slug, table):
        if slug not in table:
            out.append(f"{label}: {slug}")

    if c.race:
        check(_("Race"), c.race, reg.races)
    if c.nationality and c.nationality != "other":
        check(_("Nationality"), c.nationality, reg.nationalities)
    for t in [*c.fixed_traits, *c.random_traits]:
        check(_("Trait"), t, reg.traits)
    for s, _lvl in c.specialties:
        check(_("Specialty"), s, reg.specialties)
    for a in c.augments:
        check(_("Augment"), a, reg.augments)
    for a, _m in c.body_augments:
        check(_("Augment"), a, reg.augments)
    for s in c.stories:
        check(_("Story"), s, reg.stories)
    for i in items:
        for a, _m in i.augments or []:
            check(_("Augment"), a, reg.augments)
    return out


def import_character(data, name, password):
    """Create a new character from export data. Raises TransferError (nothing saved) on any problem."""
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise TransferError([_("This is not a TephraSheet character file.")])
    if data.get("version") != VERSION:
        raise TransferError([_("Unsupported file version {v}.", v=data.get("version"))])
    unknown = set(data) - TOP_KEYS
    if unknown:
        raise TransferError([_("Unknown keys: {names}.", names=", ".join(sorted(unknown)))])
    if len(password) < access.MIN_PASSWORD:
        raise TransferError([_("Password must have at least {n} characters.", n=access.MIN_PASSWORD)])
    errors = []
    character = _build(Character, data.get("character"), CHARACTER_SKIP, _("Character"), errors)
    rows = {}
    for key, (model, skip) in CHILDREN.items():
        values = data.get(key, [])
        if not isinstance(values, list):
            errors.append(_("{label}: not a list.", label=key))
            continue
        extra = ("weapon", "armor") if model is Automaton else ("id",) if key in ID_KEYS else ()
        rows[key] = [(r, _build(model, r, skip, f"{key} {n + 1}", errors, extra)) for n, r in enumerate(values)]
    if errors:
        raise TransferError(errors)
    items = [o for _r, o in rows["items"]]
    try:
        errors += [_("Unknown rule entry: {entry}", entry=e) for e in _unknown_slugs(character, items)]
    except (TypeError, ValueError):
        errors.append(_("The rule choices have the wrong format."))
    for n, (row, _o) in enumerate(rows["automatons"]):
        for k in ("weapon", "armor"):
            ref = row.get(k)
            if ref is not None and not (type(ref) is int and 0 <= ref < len(items)):
                errors.append(_("{label}: invalid value for {name}.", label=f"automatons {n + 1}", name=k))
    if errors:
        raise TransferError(errors)
    with transaction.atomic():
        if name:
            character.name = name[:120]
        character.set_password(password)
        character.save()
        new_ids = {prefix: {} for prefix in ID_KEYS.values()}
        for key in CHILDREN:
            for row, obj in rows[key]:
                obj.character = character
                if key == "automatons":
                    obj.weapon = items[row["weapon"]] if row.get("weapon") is not None else None
                    obj.armor = items[row["armor"]] if row.get("armor") is not None else None
                created = getattr(obj, "created", None)
                obj.save()
                if key in ID_KEYS and "id" in row:
                    new_ids[ID_KEYS[key]][row["id"]] = obj.pk
                if row.get("created"):  # keep the file's date (auto_now_add set it to now)
                    type(obj).objects.filter(pk=obj.pk).update(created=created)
        character.toggles = [k for k in map(lambda k: _remap_toggle(k, new_ids), character.toggles) if k]
        character.save(update_fields=["toggles"])
        try:  # the data must work with the rules engine, or the sheet would not open
            character.compute()
            level_history(character)
            for p in character.pets.all():
                compute_pet(p.to_state())
            for a in character.automatons.all():
                a.compute()
        except Exception:  # noqa: BLE001 – any engine error means the file does not fit the rules
            raise TransferError([_("The character data does not fit the rules (the sheet could not be computed).")])
    return character


def _remap_toggle(key, new_ids):
    """``item:<old pk>[:aug:…]``/``custom:<old pk>`` with the new pk; None for an id not in the file (it could
    match an unrelated new child)."""
    kind, _sep, rest = key.partition(":")
    old, sep, tail = rest.partition(":")
    if kind not in new_ids or not old.isdigit():
        return key
    new = new_ids[kind].get(int(old))
    return f"{kind}:{new}{sep}{tail}" if new else None


def duplicate_character(character, name, password):
    """C14: a copy with everything, through the same export → import path."""
    return import_character(export_character(character), name, password)
