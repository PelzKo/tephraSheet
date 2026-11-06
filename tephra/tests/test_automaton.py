from django.urls import reverse

from characters.models import Automaton, Character
from rules.engine.automaton import AutomatonState, compute_automaton


def test_base_values_and_augments():
    s = compute_automaton(AutomatonState(type="steamer"))
    assert (s["stats"]["hp"].total, s["stats"]["wnd"].total, s["stats"]["soak"].total) == (0, 30, 3)
    assert not s["has_ap"]
    s = compute_automaton(AutomatonState(type="steamer", core_augments=[["automata-steamer-reinforced-boiler", 2]],
                                         movement={"torso": "arms", "groin": "wheels"}))
    assert s["stats"]["wnd"].total == 50 and s["stats"]["spd"].total == 30
    assert any("Reinforced Boiler" in label for label, _v in s["stats"]["wnd"].breakdown)


def test_fusebox_ap_slots_and_specialties():
    s = compute_automaton(AutomatonState(type="fusebox"), owner_specialties=["automata-superior-brainworks"])
    assert s["stats"]["ap"].total == 3 and s["stats"]["hp"].total == 8
    s = compute_automaton(AutomatonState(type="fusebox", advanced=True))
    assert s["core_slots"] == 5
    s = compute_automaton(AutomatonState(type="fusebox", marque=2, specialties=[
        "brawl-fisticuffs", "brawl-block-with-a-grab", "agility-phase-step"]))
    assert any("2 specialties" in w for w in s["warnings"])
    s = compute_automaton(AutomatonState(type="steamer", core_augments=[["automata-fusebox-alert", 1]]))
    assert any("doesn't belong" in w for w in s["warnings"])


def test_limb_slots_and_operator(db):
    s = compute_automaton(AutomatonState(type="clockwork", limbs=[{"name": "Arm", "material": "wood", "augments": [
        ["automata-prosthetic-barbed", 1], ["automata-prosthetic-glowing", 1], ["automata-prosthetic-precision", 1]]}]))
    assert any("Arm uses 3 of 2" in w for w in s["warnings"])
    owner = Character.objects.create(race="human", specialties=[["automata-steamer-operator", 1]], skills={"Automata": 3})
    sheet = owner.compute()
    s = compute_automaton(AutomatonState(type="steamer"), ["automata-steamer-operator"], sheet.stats)
    assert s["stats"]["acc"].total == max(0, sheet.stats["acc"].total)


def test_editor_and_damage(admin_client):
    c = Character.objects.create(race="human", status="active")
    admin_client.post(reverse("automaton_new", args=[c.pk]), {"name": "Clank", "type": "fusebox", "marque": "1",
                                                               "diy": "on", "move-groin": "legs"})
    a = Automaton.objects.get()
    assert a.movement == {"groin": "legs"}
    admin_client.post(reverse("play", args=[c.pk, "auto-damage"]), {"id": a.pk, "amount": 10, "sign": "1"})
    a.refresh_from_db()
    assert (a.hp_lost, a.wounds_taken) == (8, 2)  # 8 HP, then wounds
    admin_client.post(reverse("play", args=[c.pk, "auto-damage"]), {"id": a.pk, "amount": 3, "sign": "-1"})
    a.refresh_from_db()
    assert (a.hp_lost, a.wounds_taken) == (7, 0)
    assert "Clank" in admin_client.get(c.get_absolute_url() + "?tab=pets").content.decode()
