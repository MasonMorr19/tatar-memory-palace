"""Tatar conjugation engine, ported 1:1 from the web app's vlConj() (index.html),
which was itself verified against real Tatar grammar sources (categorical vs.
indefinite future distinction, -мас/-мәс negation) and tested with 36 passing
assertions. Keep this in sync with vlConj if either changes.

Verb dict shape (matches verbLab.verbs in master_db.json):
  {id, stem, en, pron, soft, ev, vl, p3, kw, sc, [pre], [disp]}
"""

BACK_VOWELS = set("аоуыяюё")
FRONT_VOWELS = set("әеиөүэ")

TENSE_NAMES = {
    "pres": "Present tense",
    "dpast": "Definite past",
    "ipast": "Indefinite past",
    "catfut": "Categorical future",
    "auxfut": "Indefinite future",
    "cond": "Conditional mood",
    "imp": "Imperative",
}

PERSONS = [("Мин", "I"), ("Син", "you"), ("Ул", "he/she"),
           ("Без", "we"), ("Сез", "you all"), ("Алар", "they")]


def _is_vowel_final(stem):
    last = stem[-1]
    return last in BACK_VOWELS or last in FRONT_VOWELS


def conjugate(verb, tense, person, negative=False):
    """Returns (form, segments) where segments is a list of (kind, text) tuples
    for stem/pre/neg/tense/pers -- mirrors the web app's colour-coded breakdown."""
    s = verb["soft"]
    pre = verb.get("pre", "") or ""
    stem = verb["stem"]
    segs = []
    form = ""

    if tense == "pres":
        pers = ["м", "сең" if s else "сың", "", "без" if s else "быз", "сез" if s else "сыз", "ләр" if s else "лар"][person]
        if not negative:
            segs.append(("stem", verb["p3"]))
            if pers:
                segs.append(("pers", pers))
            form = verb["p3"] + pers
        else:
            nb = "ми" if s else "мый"
            segs += [("stem", stem), ("neg", nb)]
            if pers:
                segs.append(("pers", pers))
            form = stem + nb + pers

    elif tense == "dpast":
        pe = ["м", "ң", "", "к", "гез" if s else "гыз", "ләр" if s else "лар"][person]
        if not negative:
            t = ("те" if s else "ты") if verb["vl"] else ("де" if s else "ды")
            segs += [("stem", stem), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe
        else:
            n, t = ("мә" if s else "ма"), ("де" if s else "ды")
            segs += [("stem", stem), ("neg", n), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + n + t + pe

    elif tense == "ipast":
        pe = ["мен" if s else "мын", "сең" if s else "сың", "", "без" if s else "быз", "сез" if s else "сыз", "нәр" if s else "нар"][person]
        if not negative:
            t = ("кән" if s else "кан") if verb["vl"] else ("гән" if s else "ган")
            segs += [("stem", stem), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe
        else:
            t = "мәгән" if s else "маган"
            segs += [("stem", stem), ("neg", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe

    elif tense == "catfut":
        vowel_final = _is_vowel_final(stem)
        pe = ["мен" if s else "мын", "сең" if s else "сың", "", "без" if s else "быз", "сез" if s else "сыз", "ләр" if s else "лар"][person]
        if not negative:
            t = ("ячәк" if s else "ячак") if vowel_final else ("әчәк" if s else "ачак")
            segs += [("stem", stem), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe
        else:
            n = "мәячәк" if s else "маячак"
            segs += [("stem", stem), ("neg", n)]
            if pe:
                segs.append(("pers", pe))
            form = stem + n + pe

    elif tense == "auxfut":
        vowel_final = _is_vowel_final(stem)
        pe = ["мен" if s else "мын", "сең" if s else "сың", "", "без" if s else "быз", "сез" if s else "сыз", "ләр" if s else "лар"][person]
        if not negative:
            t = "р" if vowel_final else ("ер" if s else "ыр")
            segs += [("stem", stem), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe
        else:
            n = "мәс" if s else "мас"
            segs += [("stem", stem), ("neg", n)]
            if pe:
                segs.append(("pers", pe))
            form = stem + n + pe

    elif tense == "cond":
        pe = ["м", "ң", "", "к", "гез" if s else "гыз", "ләр" if s else "лар"][person]
        if not negative:
            t = "сә" if s else "са"
            segs += [("stem", stem), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + t + pe
        else:
            n, t = ("мә" if s else "ма"), ("сә" if s else "са")
            segs += [("stem", stem), ("neg", n), ("tense", t)]
            if pe:
                segs.append(("pers", pe))
            form = stem + n + t + pe

    else:  # imp
        plural = person in (3, 4, 5)
        if not negative:
            if plural:
                pl = ("гез" if s else "гыз") if verb["ev"] else ("егез" if s else "ыгыз")
                segs += [("stem", stem), ("pers", pl)]
                form = stem + pl
            else:
                segs.append(("stem", stem))
                form = stem
        else:
            n = "мә" if s else "ма"
            if plural:
                pl = "гез" if s else "гыз"
                segs += [("stem", stem), ("neg", n), ("pers", pl)]
                form = stem + n + pl
            else:
                segs += [("stem", stem), ("neg", n)]
                form = stem + n

    if pre:
        segs.insert(0, ("pre", pre.strip()))
        form = pre + form

    return form, segs
