import json
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "master_db.json")


class DataStore:
    """Thin accessor over master_db.json -- mirrors the shape the web app's
    DB object already uses (palace.stations, verbLab.verbs, vocab.*)."""

    def __init__(self, path=DEFAULT_DB_PATH):
        with open(path, encoding="utf-8") as f:
            self.raw = json.load(f)

    @property
    def stations(self):
        return self.raw["palace"]["stations"]

    @property
    def verbs(self):
        """The 71-verb peg deck (id, stem, en, pron, soft, ev, vl, p3, kw, sc, [pre], [disp])."""
        return self.raw["verbLab"]["verbs"]

    @property
    def curriculum_verbs(self):
        """The 47 curriculum verbs with full principal parts (inf/pres/cond/fut/note)."""
        return self.raw["vocab"]["verbs"]

    @property
    def nouns(self):
        return self.raw["vocab"]["nouns"]

    @property
    def expressions(self):
        return self.raw["vocab"]["expressions"]

    def verb_by_id(self, verb_id):
        return next((v for v in self.verbs if v["id"] == verb_id), None)

    def station_by_id(self, station_id):
        return next((s for s in self.stations if s["id"] == station_id), None)

    def noun_by_surface(self, surface):
        return next((n for n in self.nouns if n["s"] == surface), None)

    def verb_by_inf(self, inf):
        return next((v for v in self.curriculum_verbs if v["inf"] == inf), None)

    def resolve_gloss(self, surface):
        """Look up the English gloss for a station vocab surface form, checking
        curriculum verbs, nouns, and expressions in turn (mirrors the web app's
        wordChip() lookup order)."""
        v = self.verb_by_inf(surface)
        if v:
            return v["en"]
        n = self.noun_by_surface(surface)
        if n:
            return n["en"]
        e = next((e for e in self.expressions if e["tt"] == surface), None)
        if e:
            return e["en"]
        return ""
