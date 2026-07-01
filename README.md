# Nested Hearth — Tatar Memory Palace

A memory-first Tatar study system. One JSON spine holds **vocabulary**, **media** (lectures, books, poems, images, authentic texts), and a **memory palace** of rooms. Every drill — listening and speaking — is generated from that spine, so adding a word or a lecture once makes it show up everywhere it belongs.

> The organizing idea, borrowed from Chulpan Khismatova's CLI lecture: *Tatar as a living archive of identity, resilience, and cultural memory.* The palace is that archive made walkable.

---

## Run it

No build step. Two ways:

1. **Double-click `index.html`** — it ships with the database embedded, so it works offline and on mobile.
2. **VSCode + Live Server** (recommended for development) — right-click `index.html` → *Open with Live Server*. Served over `http://`, the app re-reads the live `data/tatar_db.json`, so edits show up on refresh.

Listening (text-to-speech) and speaking (speech recognition) work best in **Chrome** (desktop or Android). Tatar voices are rare, so the app falls back to the **Russian** engine — a phonetic approximation, not perfect, but close enough to shadow and self-check.

---

## Layout

```
tatar-palace/
├── index.html          # the Palace Studio app (data embedded; auto-refreshes from data/ over http)
├── data/
│   └── tatar_db.json    # THE SPINE — edit this; everything reads from it
└── README.md
```

`data/tatar_db.json` is the single source of truth. The pygame Memory Wheel, the Sentence Cog, the PDF Field Kit, and this app can all read the same `vocab.verbs` / `vocab.nouns` records — the schema is unchanged from `memory_wheel.py`.

---

## The spine, in three layers

**1. `vocab`** — `verbs`, `nouns`, `expressions`.
Verbs and nouns use the existing app schema (`inf/stem/vstem/pres/cls/back/en`, and `s/en/back/cat`). Each verb now also carries `cond` and `fut` example forms. Loanwords carry an **explicit** `back` flag because the last vowel lies (табип → *back*: табипка, not табипкә). `expressions` holds the somatic emotion vocabulary, idioms, **doubt/epistemic words** (бәлки, ихтимал, -дыр), **spatial postpositions** (…янында, …эчендә), and direction lines — each tagged `kind`, `somatic` (heart / head / none) and `valence`, so the rooms build themselves. Nouns now cover **directions** (`cat: Direction`) and **body parts** (`cat: Body`), the latter wired to the Heart/Head emotion idioms.

### Conjugation Forge
The app ports the verb engine from `memory_wheel.py` (vowel sets, voiceless set `пфктшсчщхцһқ`, the `vbuild` logic) into JS and adds the **conditional**. The Forge renders any verb across **present · past · future · conditional × six persons**, with a negative toggle; tap any cell to hear it. The future definite is `vstem + -ачак/-әчәк` (vowel-stems `-ячак/-ячәк`) + endings — so өйрәнү → өйрәнәчәкмен, exactly your Week 5 form.

**2. `media`** — every lecture, book, poem, image, slide, or authentic text, with an `id`. The Khismatova lecture, *Tatar Empire* (Ross), *Becoming Muslim in Imperial Russia* (Kefeli), the Miñnullin poem, Kul Sharif at night, and the Ufa flyer are all in here.

**3. `palace.stations`** — the rooms. Each station names a `locus`, then **references** vocab (by surface form), expressions, and media (by id), and supplies a `listen` and a `speak` prompt. This is where everything converges: a station is just pointers into layers 1 and 2 plus two drills.

```
station → vocab[]  ─┐
        → expressions[] ─┼─→ rendered as tappable cards
        → media[]  ──────┘
        → listen{tt,en}  → TTS
        → speak{tt,en}   → mic + similarity score
```

---

## Working with Claude Code

Point Claude Code at `data/tatar_db.json` and treat it as the contract. Useful moves:

- **"Add this week's worksheet vocab"** → append to `vocab.*`, then add or extend a station that references it. The drills appear automatically.
- **"Bind my lecture recording"** → add a `media` entry (type `lecture`, with `url`), reference its `id` from the relevant station.
- **"Generate a listening quiz for the Heart Room"** → read `stations[id].expressions`, emit prompts. No new data needed.
- Keep entries **individually** schema-valid so the pygame tools keep working: `json.load(...)["vocab"]["verbs"]` must still yield the records `memory_wheel.py` expects.

---

## Roadmap (the next few days, and after)

- **Speaking, deeper.** Add a shadow mode (play model → record → A/B playback) and a per-station streak.
- **The Ufa palace.** The *Ufa Gate* station is the bridge. Build the Bashkir-heritage layer (Lälä Tülpan, Salavat Yulaev Arena, the monument over the Belaya) as its own `palace` block, with the Ufa flyer as authentic reading.
- **Izafet layer.** Show simple vs possessive forms side by side (туган көн → туган көнем), declining only the head noun at first.
- **Feed the Sentence Cog.** Have the Cog pull its noun list from whichever station is active, so grammar practice is anchored to the room you're standing in.
- **Bashkir contrast.** A parallel column leveraging how close Bashkir and Tatar are.
- ~~**Conditional conjugator.**~~ ✅ Done — the Forge generates present/past/future/conditional live. Next: wire `-дыр` presumptive and the modal `-ган булыр иде` (contrary-to-fact) as Forge rows.

---

*Bizhbulyak → Ufa → Bashkortostan is the outer frame; the Kazan class layer is the first walkable wing. Walk the same route each time, and the wheel turns on its own.*
