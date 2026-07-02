import json
import os

# The ONE spine: the same tatar_db.json at the repo root that the web app
# embeds. This app used to carry its own data/master_db.json snapshot, which
# silently drifted (it was three versions behind by the time it was merged) --
# reading the shared spine directly means new stations, vocab, and seals show
# up here the moment they are added there.
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "tatar_db.json")


class DataStore:
    """Thin accessor over tatar_db.json -- the same shape the web app's
    DB object uses (palace.stations, verbLab.verbs, vocab.*); extra web-only
    layers (media, hearth, knowledge) are simply ignored here."""

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
        """The curriculum verbs with full principal parts (inf/pres/cond/fut/note)."""
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
