import json

from django import forms

from rules.engine.tables import VARIANTS
from rules.extensions import enabled, is_offered, offer
from rules.lang import gettext as _
from rules.registry import get_registry

from .importer import AUGMENT_LISTS_BY_KIND
from .models import ItemTemplate

FORM_FIELDS = ["name", "kind", "size", "material", "beta", "concealable", "hands", "ap_use", "ap_ready", "dc", "reach",
               "range", "increment", "soak", "eva_penalty", "spd_penalty", "climb_swim_penalty", "deflect_bonus",
               "acc_bonus", "stk_bonus", "deflect_ranged", "deflect_melee", "price_dukes", "description", "memento",
               "binding"]


class ItemForm(forms.ModelForm):
    """Object creator. Empty numbers mean "use the rules' size table"."""

    variants = forms.MultipleChoiceField(choices=[(k, v["label"]) for k, v in VARIANTS.items()], required=False,
                                         widget=forms.CheckboxSelectMultiple)
    augments_json = forms.CharField(required=False, widget=forms.HiddenInput)
    price_princes = forms.DecimalField(required=False, min_value=0, decimal_places=1)

    class Meta:
        model = ItemTemplate
        fields = FORM_FIELDS + ["is_starting_gear"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, gm=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not gm:
            self.fields.pop("is_starting_gear")
        self.fields.pop("price_dukes")
        self.fields["price_princes"].label = _("Price (princes)")
        inst = self.instance
        if inst and inst.pk or (inst and inst.name):
            self.initial["variants"] = inst.variants
            self.initial["augments_json"] = json.dumps(inst.augments or [])
            self.initial["price_princes"] = (inst.price_dukes or 0) / 10
        if "mementos" not in enabled() and not inst.memento:  # fields of an extension (Mementos)
            self.fields.pop("memento")
            self.fields.pop("binding")
        for kind, ext in (("resonator", "aether"), ("living-liquid", "living-liquids")):  # kinds of extensions
            if ext not in enabled() and inst.kind != kind:
                self.fields["kind"].choices = [c for c in self.fields["kind"].choices if c[0] != kind]
        self.fields["variants"].choices = [(k, v["label"]) for k, v in VARIANTS.items()
                                           if is_offered(v) or k in (inst.variants or [])]
        for name in ("ap_use", "ap_ready", "dc", "reach", "range", "increment", "soak", "eva_penalty",
                     "spd_penalty", "climb_swim_penalty", "deflect_bonus"):
            self.fields[name].widget.attrs["placeholder"] = "auto"

    def clean_augments_json(self):
        raw = self.cleaned_data.get("augments_json") or "[]"
        try:
            data = json.loads(raw)
        except ValueError:
            raise forms.ValidationError(_("Invalid augment data."))
        reg = get_registry()
        out = []
        for entry in data:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                continue
            slug, marque = entry
            if slug in reg.augments:
                out.append([slug, max(1, min(4, int(marque)))])
        return out

    def clean(self):
        data = super().clean()
        augs = data.get("augments_json") or []
        kind = data.get("kind")
        reg = get_registry()
        lists = AUGMENT_LISTS_BY_KIND.get(kind)
        used = memento_used = 0
        for slug, _marque in augs:
            aug = reg.augments[slug]
            if "memento" in aug["lists"]:  # Luck augments, independent of the item's own slots
                if not data.get("memento"):
                    self.add_error(None, _("{augment} only fits a memento.", augment=aug["name"]))
                memento_used += aug.get("slots") or 0
                continue
            if lists and not lists.intersection(aug["lists"]):
                self.add_error(None, _("{augment} can't be placed on a {kind}.", augment=aug["name"], kind=kind))
            elif "turret" in aug["lists"] and "turret" not in (data.get("variants") or []):
                self.add_error(None, _("{augment} only fits a turret.", augment=aug["name"]))
            used += aug.get("slots") or 0
        tmp = ItemTemplate(kind=kind or "", material=data.get("material") or "metal", beta=bool(data.get("beta")))
        if memento_used > 3 + (2 if data.get("beta") else 0):
            self.add_error(None, _("Memento augments need {used} slots, a memento has {slots}.", used=memento_used,
                                   slots=3 + (2 if data.get("beta") else 0)))
        if used > tmp.slot_count:
            self.add_error(None, _("Augments need {used} slots, the item has {slots}.", used=used, slots=tmp.slot_count))
        return data

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.variants = self.cleaned_data.get("variants") or []
        obj.augments = self.cleaned_data.get("augments_json") or []
        price = self.cleaned_data.get("price_princes")
        obj.price_dukes = int(round(float(price or 0) * 10))
        if commit:
            obj.save()
        return obj


def augment_choices_json():
    """Augment options per item kind for the creator's picker."""
    reg = get_registry()
    out = {}
    for kind, lists in [*AUGMENT_LISTS_BY_KIND.items(), ("memento", {"memento"})]:
        out[kind] = [{"slug": a["slug"], "name": a["name"], "slots": a.get("slots") or 0,
                      "marques": a["marques"], "list": "/".join(a["lists"]), "notes": a["notes"],
                      "text": a["text"], "two_marque": a.get("two_marque", False)}
                     for a in offer(reg.augments.values()) if lists.intersection(a["lists"])]
    return out
