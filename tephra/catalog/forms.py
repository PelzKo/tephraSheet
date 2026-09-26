import json

from django import forms

from rules.engine.tables import VARIANTS
from rules.registry import get_registry

from .importer import AUGMENT_LISTS_BY_KIND
from .models import ItemTemplate

FORM_FIELDS = ["name", "kind", "size", "material", "beta", "concealable", "ap_use", "ap_ready", "dc", "reach",
               "range", "increment", "soak", "eva_penalty", "spd_penalty", "climb_swim_penalty", "deflect_bonus",
               "deflect_ranged", "deflect_melee", "price_dukes", "description"]


class ItemForm(forms.ModelForm):
    """Object creator. Empty numbers mean "use the rules' size table"."""

    variants = forms.MultipleChoiceField(choices=[(k, v["label"]) for k, v in VARIANTS.items()], required=False,
                                         widget=forms.CheckboxSelectMultiple)
    augments_json = forms.CharField(required=False, widget=forms.HiddenInput)
    price_princes = forms.DecimalField(required=False, min_value=0, decimal_places=1, label="Price (princes)")

    class Meta:
        model = ItemTemplate
        fields = FORM_FIELDS + ["is_starting_gear"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, gm=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not gm:
            self.fields.pop("is_starting_gear")
        self.fields.pop("price_dukes")
        inst = self.instance
        if inst and inst.pk or (inst and inst.name):
            self.initial["variants"] = inst.variants
            self.initial["augments_json"] = json.dumps(inst.augments or [])
            self.initial["price_princes"] = (inst.price_dukes or 0) / 10
        for name in ("ap_use", "ap_ready", "dc", "reach", "range", "increment", "soak", "eva_penalty",
                     "spd_penalty", "climb_swim_penalty", "deflect_bonus"):
            self.fields[name].widget.attrs["placeholder"] = "auto"

    def clean_augments_json(self):
        raw = self.cleaned_data.get("augments_json") or "[]"
        try:
            data = json.loads(raw)
        except ValueError:
            raise forms.ValidationError("Invalid augment data.")
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
        used = 0
        for slug, _ in augs:
            aug = reg.augments[slug]
            if lists and not lists.intersection(aug["lists"]):
                self.add_error(None, f"{aug['name']} can't be placed on a {kind}.")
            used += aug.get("slots") or 0
        tmp = ItemTemplate(material=data.get("material") or "metal", beta=bool(data.get("beta")))
        if used > tmp.slot_count:
            self.add_error(None, f"Augments need {used} slots, the item has {tmp.slot_count}.")
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
    for kind, lists in AUGMENT_LISTS_BY_KIND.items():
        out[kind] = [{"slug": a["slug"], "name": a["name"], "slots": a.get("slots") or 0,
                      "marques": a["marques"], "list": "/".join(a["lists"])}
                     for a in reg.augments.values() if lists.intersection(a["lists"])]
    return out
